import asyncio
import json
import time
from time import sleep
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from openai import OpenAI
from chat.models import ChatSessionModel, ChatMessageModel
from chat.serializers import ChatMessageSerializer
from xazna import settings
from xazna.consumers import BaseWebsocketConsumer

openai_api_key = "EMPTY"
openai_api_base = settings.LLM_SERVER
client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)


class ChatConsumer(BaseWebsocketConsumer):
    auth_required = True

    async def on_connect(self):
        self.session = await database_sync_to_async(ChatSessionModel.objects.get)(
            id=self.scope["url_route"]["kwargs"]["session_id"],
            user=self.user
        )
        self.contents = await database_sync_to_async(lambda: ChatMessageSerializer(
            self.session.messages
            .exclude(role="system")
            .order_by("created_at")
            .values("role", "content"),
            many=True
        ).data)()

        self.stream_task = None
        self.assistant_content = ""

        if self.session.is_streaming and len(self.contents) == 1:
            self.session.is_streaming = False
            await database_sync_to_async(self.session.save)()
            self.stream_task = asyncio.create_task(self._stream_llm())

    async def on_receive(self, request):
        data = json.loads(request)
        action = data.get("action")

        if action == "cancel":
            if self.stream_task is not None and not self.stream_task.done():
                self.stream_task.cancel()

                if self.assistant_content != "":
                   await self._create_message(role="assistant", content=self.assistant_content)
                   self.contents.append({"role": "assistant", "content": self.assistant_content})
                   self.assistant_content = ""
            return


        self.assistant_content = ""
        self.session.is_streaming = True

        await database_sync_to_async(self.session.save)()

        if self.session is None:
            await self.send(json.dumps({
                "status": 404,
                "type": "error",
                "message": "Session not found."
            }))

            return

        user_content = data.get("content")

        if not user_content:
            return

        last_message = self.contents[-1] if self.contents else None
        if last_message is not None and last_message["role"] == "user":
            print(self.contents)

            print(last_message)
            await self._create_message(role="assistant", error="Failed to connect llm.")
            self.contents.append({"role": "assistant", "content": None})

        await self._create_message(role="user", content=user_content)

        self.contents.append({"role": "user", "content": user_content})

        self.stream_task = asyncio.create_task(self._stream_llm())


    async def _stream_llm(self):
        min_interval = 0.005
        last_sent_time = 0

        try:
            conversation = [
                {"role": "user",
                 "content": "Senga o'zbek tilida murojaat qilishadi. Sen faqat o'zbek tilida gaplashishing kerak."},
                {"role": "assistant", "content": "Albatta! Faqat o'zbek tilida javob qaytaraman."},
                *self.contents
            ]

            model = client.models.list().data[0].id

            stream = client.chat.completions.create(
                model=model,
                messages=conversation,
                stream=True,
                temperature=0.7,
            )

            await self.send(json.dumps({"status": "started"}))

            for chunk in stream:
                delta = chunk.choices[0].delta

                if delta.content:
                    for ch in delta.content:
                        now = time.monotonic()
                        elapsed = now - last_sent_time
                        if elapsed < min_interval:
                            await asyncio.sleep(min_interval - elapsed)

                        await self.send(json.dumps({
                            "status": "pending",
                            "type": "stream",
                            "token": ch
                        }))
                        last_sent_time = time.monotonic()

                    self.assistant_content += delta.content

            self.contents.append({"role": "assistant", "content": self.assistant_content})
            await self._create_message(role="assistant", content=self.assistant_content)
            await self.send(json.dumps({"status": "completed"}))

        except Exception as e:
            await self.send(json.dumps({
                "status": "failed",
                "type": "error",
                "message": str(e)
            }))
            await self._create_message(role="assistant", error=e)
            self.contents.append({"role": "assistant", "content": None})
            await self.send(json.dumps({"status": "failed"}))
        finally:
            self.session.is_streaming = False
            await database_sync_to_async(self.session.save)()


    @sync_to_async
    def _create_message(self, role, content=None, error=None):
        ChatMessageModel.objects.create(
            session=self.session,
            role=role,
            content=content,
            error=error
        )

    async def disconnect(self, close_code):
        print(f"""Disconnected: {close_code}""")
        if self.stream_task and not self.stream_task.done():
            if self.assistant_content != "":
                await self._create_message(role="assistant", content=self.assistant_content)

            self.stream_task.cancel()

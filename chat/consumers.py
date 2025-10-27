import asyncio
import json
import time
from time import sleep

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from openai import OpenAI
from chat.models import ChatSessionModel, ChatMessageModel
from chat.serializers import ChatSessionSerializer, ChatMessageSerializer
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
            .values("role", "content"),
            many=True
        ).data)()

    async def on_receive(self, text_data):

        if self.session is None:
            await self.send(json.dumps({
                "status": 404,
                "type": "error",
                "message": "Session not found."
            }))

            return

        data = json.loads(text_data)
        user_content = data.get("content")

        if not user_content:
            return

        await self._create_message(role="user", content=user_content)

        self.contents.append({"role": "user", "content": user_content})

        await self.send(json.dumps({"status": "started"}))

        # await self._stream_llm()
        asyncio.create_task(self._stream_llm())


    async def _stream_llm(self):
        min_interval = 0.02
        last_sent_time = 0
        assistant_content = ""

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
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    now = time.monotonic()
                    elapsed = now - last_sent_time
                    if elapsed < min_interval:
                        await asyncio.sleep(min_interval - elapsed)

                    await self.send(json.dumps({
                        "status": "pending",
                        "type": "stream",
                        "token": delta.content
                    }))
                    assistant_content += delta.content
                    last_sent_time = time.monotonic()

            await self._create_message(role="assistant", content=assistant_content)
            await self.send(json.dumps({"status": "completed"}))
        except Exception as e:
            await self.send(json.dumps({
                "status": "failed",
                "type": "error",
                "message": str(e)
            }))
            await self._create_message(role="assistant", error=e)
            await self.send(json.dumps({"status": "failed"}))
        finally:
            self.contents.append({"role": "assistant", "content": assistant_content})

    @sync_to_async
    def _create_message(self, role, content=None, error=None):
        ChatMessageModel.objects.create(
            session=self.session,
            role=role,
            content=content,
            error=error
        )

    async def disconnect(self, close_code):

        print(f"Disconnected: {close_code}")

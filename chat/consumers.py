import asyncio
import json
import time
from time import sleep

from asgiref.sync import sync_to_async
from openai import OpenAI
from chat.models import ChatSessionModel, ChatMessageModel
from xazna import settings
from xazna.consumers import BaseWebsocketConsumer

openai_api_key = "EMPTY"
openai_api_base = settings.LLM_SERVER
client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)


def stream_llm_response(conversation):
    model = client.models.list().data[0].id

    stream = client.chat.completions.create(
        model=model,
        messages=conversation,
        stream=True,
        temperature=0.7,
        max_tokens=200,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


class ChatConsumer(BaseWebsocketConsumer):
    auth_required = True

    async def handle_receive(self, text_data):
        user = self.scope["user"]
        print(user)
        self.session = ChatSessionModel.objects.filter(id=self.scope["url_route"]["kwargs"]["session_id"], user=user).first()

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


        await self.create_message(role="user", content=user_content)

        conversation = [
            {"role": "user",
             "content": "Senga o'zbek tilida murojaat qilishadi. Sen faqat o'zbek tilida gaplashishing kerak."},
            {"role": "assistant", "content": "Albatta! Faqat o'zbek tilida javob qaytaraman."},
            {"role": "user", "content": user_content},
        ]

        assistant_content = ""

        await self.send(json.dumps({"status": "started"}))

        try:
            min_interval = 0.02
            last_sent_time = 0
            for token in stream_llm_response(conversation):
                now = time.monotonic()
                elapsed = now - last_sent_time
                if elapsed < min_interval:
                    await asyncio.sleep(min_interval - elapsed)

                await self.send(json.dumps({
                    "status": "pending",
                    "type": "stream",
                    "token": token
                }))
                assistant_content += token
                last_sent_time = time.monotonic()


            await self.create_message(role="assistant", content=assistant_content)
            await self.send(json.dumps({"status": "completed"}))

        except Exception as e:
            await self.create_message(role="assistant", error=e, status="failed")
            await self.send(json.dumps({"status": "failed"}))


    @sync_to_async
    def create_message(self, role, content=None, status="completed", error=None):
        ChatMessageModel.objects.create(
            session=self.session,
            role=role,
            content=content,
            status=status,
            error=error
        )

    async def disconnect(self, close_code):
        print(f"Disconnected: {close_code}")
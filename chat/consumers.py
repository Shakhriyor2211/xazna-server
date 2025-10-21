import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from chat.models import ChatSessionModel, ChatMessageModel
from openai import OpenAI
from xazna import settings

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



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnected: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_content = data.get("content")

        if not user_content:
            return

        await self.create_message(role="user", content=user_content)

        conversation = [
            {"role": "user", "content": "Senga o'zbek tilida murojaat qilishadi. Sen faqat o'zbek tilida gaplashishing kerak."},
            {"role": "assistant", "content": "Albatta! Faqat o'zbek tilida javob qaytaraman."},
            {"role": "user", "content": user_content},
        ]

        assistant_content = ""

        await self.send(json.dumps({"status": "started"}))

        try:
            for token in stream_llm_response(conversation):
                await self.send(json.dumps({
                    "type": "stream",
                    "token": token
                }))
                assistant_content += token

            await self.create_message(role="assistant", content=assistant_content)
            await self.send(json.dumps({"status": "completed"}))


        except Exception as e:
            print(e)
            await self.create_message(role="assistant", error=e, status="failed")
            await self.send(json.dumps({"status": "failed"}))


    @sync_to_async
    def create_message(self, role, content=None, status="completed", error=None):
        session = ChatSessionModel.objects.get(id=self.session_id)
        ChatMessageModel.objects.create(
            session=session,
            role=role,
            content=content,
            status=status,
            error=error
        )
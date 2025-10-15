import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from chat.models import ChatSessionModel, ChatMessageModel
from chat.serializers import ChatMessageSerializer



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.room_group_name = f"""chat_{self.session_id}"""

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_content = data.get("content")

        if not user_content:
            return

        user_msg = await self.create_message(role="user", content=user_content)

        assistant_content = f"""Assistant reply to: {user_content}"""

        assistant_msg = await self.create_message(role="assistant", content=assistant_content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": user_msg,
                "assistant": assistant_msg,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "user": event["user"],
            "assistant": event["assistant"]
        }))

    @sync_to_async
    def create_message(self, role, content):
        session = ChatSessionModel.objects.get(id=self.session_id)
        message = ChatMessageModel.objects.create(
            session=session,
            role=role,
            content=content,
            status="pending",
        )

        return ChatMessageSerializer(message).data


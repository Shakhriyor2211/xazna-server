from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.http import parse_cookie
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from accounts.models import CustomUserModel
from xazna import settings


class BaseWebsocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        auth_required = getattr(self, "auth_required", False)

        if not auth_required:
            self.scope["user"] = AnonymousUser()
            return None

        cookies = {}

        for name, value in self.scope.get("headers", []):
            if name == b"cookie":
                cookies = parse_cookie(value.decode("latin1"))
                break

        token = cookies.get("access_token")

        if not token:
            await self.close(code=4001)

        try:
            payload = decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True}
            )

            user_id = payload.get("user_id") or payload.get("sub")
            user = await database_sync_to_async(CustomUserModel.objects.get)(id=user_id)

            if user.is_blocked:
                await self.close(code=4003)

            admin_required = getattr(self, "admin_required", False)

            if admin_required and user.role != "admin" and user.role != "superadmin":
                await self.close(code=4003)

            self.scope["user"] = user

        except ExpiredSignatureError:
            await self.close(code=4001)
        except InvalidTokenError:
            await self.close(code=4000)
        except CustomUserModel.DoesNotExist:
            await self.close(code=4000)
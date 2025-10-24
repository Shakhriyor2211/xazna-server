import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.http import parse_cookie
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from accounts.models import CustomUserModel
from xazna import settings


class BaseWebsocketConsumer(AsyncWebsocketConsumer):
    async def _validate(self):
        auth_required = getattr(self, "auth_required", False)

        if not auth_required:
            self.scope["user"] = AnonymousUser()
            return True

        cookies = {}

        for name, value in self.scope.get("headers", []):
            if name == b"cookie":
                cookies = parse_cookie(value.decode("latin1"))
                break

        token = cookies.get("access_token")

        if not token:
            await self.close(code=4400)

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
                await self.send(json.dumps({
                    "status": 403,
                    "type": "error",
                    "message": "Account is blocked."
                }))
                return False

            admin_required = getattr(self, "admin_required", False)

            if admin_required and user.role != "admin" and user.role != "superadmin":
                await self.send(json.dumps({
                    "status": 403,
                    "type": "error",
                    "message": "Admin privileges required."
                }))
                return False

            self.scope["user"] = user

        except ExpiredSignatureError:
            await self.send(json.dumps({
                "status": 401,
                "type": "error",
                "message": "Token has expired."
            }))
            return False

        except InvalidTokenError:
            await self.close(code=4400)
            return False
        except CustomUserModel.DoesNotExist:
            await self.close(code=4404)
            return False

    async def connect(self):
        await self.accept()
        await self._validate()

    async def receive(self, text_data=None, bytes_data=None):
        is_valid = await self._validate()
        if not is_valid:
            return

        if hasattr(self, "handle_receive"):
            await self.handle_receive(text_data, bytes_data)

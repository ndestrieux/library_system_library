from typing import Any

from strawberry import Info
from strawberry.permission import BasePermission

from jwt_token_manager import JWTToken


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        request = info.context["request"]
        authentication = request.headers.get("authentication")
        if authentication:
            token = authentication.split()[-1]
            auth_result = JWTToken.decode(token)
            info.context["requester_data"] = auth_result.model_dump()
            return True
        return False


class HasAdminGroup(BasePermission):
    message = "User is not admin"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        if "admin" in info.context["requester_data"]["groups"]:
            return True
        return False

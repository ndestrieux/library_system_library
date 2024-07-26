from typing import Any

from strawberry import Info
from strawberry.permission import BasePermission

from utils import get_requester, get_requester_groups


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        return bool(get_requester(info))


class HasAdminGroup(BasePermission):
    message = "User is not admin"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        requester_groups = get_requester_groups(info)
        if requester_groups:
            return "admin" in get_requester_groups(info)
        return False

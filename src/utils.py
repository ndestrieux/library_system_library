from typing import List

from strawberry import Info


def get_requester(info: Info) -> str:
    return info.context["request"].headers.get("requester")


def get_requester_groups(info: Info) -> List[str]:
    return info.context["request"].headers.get("groups")

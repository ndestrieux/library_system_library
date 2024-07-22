from strawberry import Info


def get_requester(info: Info) -> str:
    return info.context["request"].headers.get("requester")

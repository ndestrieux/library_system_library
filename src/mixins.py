import strawberry


class InputAsDictMixin:
    def asdict(self):
        return {
            k: v for k, v in strawberry.asdict(self).items() if v != strawberry.UNSET
        }

from datetime import date
from typing import Optional

import strawberry


@strawberry.type
class AdminExtraFields:
    created_by: str
    created_on: date
    last_updated_by: Optional[str]
    last_updated_on: Optional[date]

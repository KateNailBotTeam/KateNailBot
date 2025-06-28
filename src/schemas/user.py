from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: Annotated[
        int, Field(gt=0, description="user telegram id", examples=[123456789])
    ]
    username: Annotated[
        str | None,
        Field(
            default=None,
            min_length=2,
            max_length=50,
            description="Telegram username without @",
        ),
    ]
    first_name: Annotated[str, Field(max_length=100, description="User's first name")]
    last_name: Annotated[
        str | None, Field(default=None, max_length=100, description="User's last name")
    ]
    phone: Annotated[
        str | None,
        Field(
            default=None,
            max_length=20,
            description="Phone number in format +7**********",
            examples=["+79001002030"],
        ),
    ]
    is_admin: Annotated[bool, Field(default=False, description="Has admin roots")]
    created_at: Annotated[datetime, Field(..., title="date of creating")]
    updated_at: Annotated[
        datetime | None, Field(default=None, title="date of updating")
    ]

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Schedule:

    id: Optional[int]

    user_id: int

    channel_id: str

    message_type: str

    file_id: Optional[str]

    text: Optional[str]

    send_datetime: str

    status: int = 0

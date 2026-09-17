from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ProgramItem:
    id: int | None
    channel_id: int
    external_id: str | None
    title: str
    start_at: datetime
    end_at: datetime
    category: str | None = None
    description: str | None = None
    subtitle: str | None = None

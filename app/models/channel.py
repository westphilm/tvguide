from dataclasses import dataclass


@dataclass(slots=True)
class Channel:
    id: int | None
    name: str
    short_name: str
    sort_index: int
    enabled: bool = True

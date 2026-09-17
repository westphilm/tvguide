from dataclasses import dataclass


@dataclass(slots=True)
class ChannelGroup:
    id: int | None
    name: str
    sort_index: int

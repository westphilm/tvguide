from dataclasses import dataclass

from app.models.channel import Channel
from app.models.program_item import ProgramItem


@dataclass(slots=True)
class ProgramOverview:
    channel: Channel
    current_program: ProgramItem | None
    next_program: ProgramItem | None
    following_program: ProgramItem | None

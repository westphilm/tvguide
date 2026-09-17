from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.models.channel import Channel
from app.models.program_item import ProgramItem


class ProgramProvider(ABC):
    @abstractmethod
    def get_program(self, channel: Channel, now: datetime) -> list[ProgramItem]:
        raise NotImplementedError

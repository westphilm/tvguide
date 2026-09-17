from __future__ import annotations

from datetime import datetime

from app.db.program_repository import ProgramRepository
from app.models.channel import Channel
from app.models.program_item import ProgramItem
from app.models.program_overview import ProgramOverview
from app.providers.base import ProgramProvider


class ProgramService:
    def __init__(self, repository: ProgramRepository, provider: ProgramProvider) -> None:
        self.repository = repository
        self.provider = provider

    def refresh(self, channels: list[Channel], now: datetime) -> None:
        for channel in channels:
            if channel.id is None:
                continue
            if self.repository.was_refreshed_today(channel.id, now):
                continue
            try:
                items = self.provider.get_program(channel, now)
            except OSError:
                continue
            self.repository.replace_for_channel(channel.id, items, refreshed_at=now)

    def build_overviews(self, channels: list[Channel], now: datetime) -> list[ProgramOverview]:
        overviews: list[ProgramOverview] = []

        for channel in channels:
            if channel.id is None:
                continue
            items = self.repository.list_for_channel(channel.id)
            current = self._find_current(items, now)
            next_program = self._find_next(items, now, current)
            following_program = self._find_next(items, now, next_program)
            overviews.append(
                ProgramOverview(
                    channel=channel,
                    current_program=current,
                    next_program=next_program,
                    following_program=following_program,
                )
            )

        return overviews

    @staticmethod
    def _find_current(items: list[ProgramItem], now: datetime) -> ProgramItem | None:
        return next((item for item in items if item.start_at <= now < item.end_at), None)

    @staticmethod
    def _find_next(
        items: list[ProgramItem],
        now: datetime,
        current: ProgramItem | None,
    ) -> ProgramItem | None:
        threshold = current.end_at if current else now
        return next((item for item in items if item.start_at >= threshold), None)

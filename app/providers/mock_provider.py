from __future__ import annotations

from datetime import datetime, timedelta

from app.models.channel import Channel
from app.models.program_item import ProgramItem
from app.providers.base import ProgramProvider


class MockProgramProvider(ProgramProvider):
    _TITLES = {
        'ARD': ('Tagesschau kompakt', 'Tatort', 'Tagesthemen'),
        'ZDF': ('heute', 'Der Fernsehfilm der Woche', 'heute journal'),
        'ARTE': ('Arte Journal', 'Dokumentation', 'Tracks East'),
        '3SAT': ('Kulturzeit', 'Wissen aktuell', 'nano'),
        'PHOENIX': ('phoenix vor ort', 'Dokumentation', 'phoenix der tag'),
    }

    def get_program(self, channel: Channel, now: datetime) -> list[ProgramItem]:
        if channel.id is None:
            raise ValueError('Channel must be persisted')

        titles = self._TITLES.get(
            channel.short_name.upper(),
            ('Aktuelle Sendung', 'Hauptprogramm', 'Spätprogramm'),
        )

        current_start = now.replace(second=0, microsecond=0) - timedelta(minutes=20)
        current_end = current_start + timedelta(minutes=55)

        slots = [
            (titles[0], current_start - timedelta(minutes=30), current_start, 'Info'),
            (titles[1], current_start, current_end, 'Programm'),
            (titles[2], current_end, current_end + timedelta(minutes=45), 'Info'),
            ('Nachtprogramm', current_end + timedelta(minutes=45), current_end + timedelta(minutes=90), 'Programm'),
        ]

        return [
            ProgramItem(
                id=None,
                channel_id=channel.id,
                external_id=f'mock:{channel.short_name}:{index}',
                title=title,
                start_at=start,
                end_at=end,
                category=category,
            )
            for index, (title, start, end, category) in enumerate(slots)
        ]

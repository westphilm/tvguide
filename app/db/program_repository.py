from __future__ import annotations

from datetime import datetime

from app.db.database import Database
from app.models.program_item import ProgramItem


class ProgramRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def _serialize(value: datetime) -> str:
        return value.isoformat(timespec='seconds')

    @staticmethod
    def _deserialize(value: str) -> datetime:
        return datetime.fromisoformat(value)

    def replace_for_channel(
        self,
        channel_id: int,
        items: list[ProgramItem],
        refreshed_at: datetime | None = None,
    ) -> None:
        with self.database.transaction() as connection:
            connection.execute('DELETE FROM program_items WHERE channel_id = ?', (channel_id,))
            connection.executemany(
                '''INSERT INTO program_items(
                       channel_id, external_id, title, start_at, end_at, category, description, subtitle
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                [
                    (
                        item.channel_id,
                        item.external_id,
                        item.title,
                        self._serialize(item.start_at),
                        self._serialize(item.end_at),
                        item.category,
                        item.description,
                        item.subtitle,
                    )
                    for item in items
                ],
            )
            if refreshed_at:
                connection.execute(
                    '''INSERT INTO program_refreshes(channel_id, refreshed_at)
                       VALUES (?, ?)
                       ON CONFLICT(channel_id) DO UPDATE SET refreshed_at = excluded.refreshed_at''',
                    (channel_id, self._serialize(refreshed_at)),
                )

    def was_refreshed_today(self, channel_id: int, now: datetime) -> bool:
        with self.database.connect() as connection:
            row = connection.execute(
                'SELECT refreshed_at FROM program_refreshes WHERE channel_id = ?',
                (channel_id,),
            ).fetchone()

        return bool(row and self._deserialize(row['refreshed_at']).date() == now.date())

    def list_for_channel(self, channel_id: int) -> list[ProgramItem]:
        with self.database.connect() as connection:
            rows = connection.execute(
                '''SELECT id, channel_id, external_id, title, start_at, end_at, category, description, subtitle
                   FROM program_items
                   WHERE channel_id = ?
                   ORDER BY start_at''',
                (channel_id,),
            ).fetchall()

        return [
            ProgramItem(
                id=row['id'],
                channel_id=row['channel_id'],
                external_id=row['external_id'],
                title=row['title'],
                start_at=self._deserialize(row['start_at']),
                end_at=self._deserialize(row['end_at']),
                category=row['category'],
                description=row['description'],
                subtitle=row['subtitle'],
            )
            for row in rows
        ]

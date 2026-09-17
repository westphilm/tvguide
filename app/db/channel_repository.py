from __future__ import annotations

import sqlite3

from app.db.database import Database
from app.models.channel import Channel


class ChannelRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Channel:
        return Channel(
            id=row['id'],
            name=row['name'],
            short_name=row['short_name'],
            sort_index=row['sort_index'],
            enabled=bool(row['enabled']),
        )

    def list_enabled(self) -> list[Channel]:
        with self.database.connect() as connection:
            rows = connection.execute(
                '''SELECT id, name, short_name, sort_index, enabled
                   FROM channels
                   WHERE enabled = 1
                   ORDER BY sort_index, id'''
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def list_all(self) -> list[Channel]:
        with self.database.connect() as connection:
            rows = connection.execute(
                '''SELECT id, name, short_name, sort_index, enabled
                   FROM channels
                   ORDER BY sort_index, id'''
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def insert(self, channel: Channel) -> Channel:
        with self.database.transaction() as connection:
            cursor = connection.execute(
                '''INSERT INTO channels(name, short_name, sort_index, enabled)
                   VALUES (?, ?, ?, ?)''',
                (channel.name, channel.short_name, channel.sort_index, int(channel.enabled)),
            )
            channel.id = int(cursor.lastrowid)
        return channel

    def update_sort_order(self, channels: list[Channel]) -> None:
        with self.database.transaction() as connection:
            for index, channel in enumerate(channels):
                if channel.id is None:
                    raise ValueError('Channel must be persisted before sorting')
                connection.execute(
                    'UPDATE channels SET sort_index = ? WHERE id = ?',
                    (index, channel.id),
                )
                channel.sort_index = index

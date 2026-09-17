from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys = ON')
        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.transaction() as connection:
            connection.executescript(
                '''
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    short_name TEXT NOT NULL UNIQUE,
                    sort_index INTEGER NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS program_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    external_id TEXT,
                    title TEXT NOT NULL,
                    start_at TEXT NOT NULL,
                    end_at TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_channels_sort
                    ON channels(enabled, sort_index);

                CREATE INDEX IF NOT EXISTS idx_program_items_channel_time
                    ON program_items(channel_id, start_at, end_at);

                CREATE TABLE IF NOT EXISTS program_refreshes (
                    channel_id INTEGER PRIMARY KEY,
                    refreshed_at TEXT NOT NULL,
                    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS channel_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sort_index INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS channel_group_members (
                    group_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    PRIMARY KEY(group_id, channel_id),
                    FOREIGN KEY(group_id) REFERENCES channel_groups(id) ON DELETE CASCADE,
                    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
                );
                '''
            )
            columns = {
                row['name']
                for row in connection.execute('PRAGMA table_info(program_items)').fetchall()
            }
            if 'subtitle' not in columns:
                connection.execute('ALTER TABLE program_items ADD COLUMN subtitle TEXT')

from app.db.database import Database
from app.models.channel import Channel
from app.models.channel_group import ChannelGroup


class ChannelGroupRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def list_groups(self) -> list[ChannelGroup]:
        with self.database.connect() as connection:
            rows = connection.execute('SELECT id, name, sort_index FROM channel_groups ORDER BY sort_index, id').fetchall()
        return [ChannelGroup(row['id'], row['name'], row['sort_index']) for row in rows]

    def create(self, name: str, channel_ids: list[int]) -> ChannelGroup:
        with self.database.transaction() as connection:
            sort_index = connection.execute('SELECT COUNT(*) FROM channel_groups').fetchone()[0]
            cursor = connection.execute('INSERT INTO channel_groups(name, sort_index) VALUES (?, ?)', (name, sort_index))
            group = ChannelGroup(int(cursor.lastrowid), name, sort_index)
            self._replace_members(connection, group.id, channel_ids)
        return group

    def replace_members(self, group_id: int, channel_ids: list[int]) -> None:
        with self.database.transaction() as connection:
            self._replace_members(connection, group_id, channel_ids)

    def rename(self, group_id: int, name: str) -> None:
        with self.database.transaction() as connection:
            connection.execute('UPDATE channel_groups SET name = ? WHERE id = ?', (name, group_id))

    @staticmethod
    def _replace_members(connection, group_id: int | None, channel_ids: list[int]) -> None:
        if group_id is None:
            raise ValueError('Group must be persisted')
        connection.execute('DELETE FROM channel_group_members WHERE group_id = ?', (group_id,))
        connection.executemany('INSERT INTO channel_group_members(group_id, channel_id) VALUES (?, ?)', [(group_id, channel_id) for channel_id in channel_ids])

    def list_channels(self, group_id: int) -> list[Channel]:
        with self.database.connect() as connection:
            rows = connection.execute('''SELECT c.id, c.name, c.short_name, c.sort_index, c.enabled
                                       FROM channels c
                                       JOIN channel_group_members m ON m.channel_id = c.id
                                       WHERE m.group_id = ?
                                       ORDER BY c.sort_index, c.id''', (group_id,)).fetchall()
        return [Channel(row['id'], row['name'], row['short_name'], row['sort_index'], bool(row['enabled'])) for row in rows]

    def member_ids(self, group_id: int) -> list[int]:
        with self.database.connect() as connection:
            rows = connection.execute('SELECT channel_id FROM channel_group_members WHERE group_id = ?', (group_id,)).fetchall()
        return [row['channel_id'] for row in rows]

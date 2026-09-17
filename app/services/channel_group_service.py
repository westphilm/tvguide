from app.config.channel_catalog import PUBLIC_BROADCASTERS
from app.db.channel_group_repository import ChannelGroupRepository
from app.models.channel import Channel
from app.models.channel_group import ChannelGroup


class ChannelGroupService:
    def __init__(self, repository: ChannelGroupRepository) -> None:
        self.repository = repository

    def ensure_defaults(self, channels: list[Channel]) -> None:
        groups = self.repository.list_groups()
        if groups:
            public_group = next((group for group in groups if group.name == 'Öffentlich-rechtlich'), None)
            added_channel_ids = [
                channel.id
                for channel in channels
                if channel.short_name in {'ZDFINFO', 'ZDFNEO'} and channel.id is not None
            ]
            if public_group and public_group.id is not None:
                member_ids = self.repository.member_ids(public_group.id)
                new_member_ids = [channel_id for channel_id in added_channel_ids if channel_id not in member_ids]
                if new_member_ids:
                    self.repository.replace_members(public_group.id, [*member_ids, *new_member_ids])
            return
        public_ids = [channel.id for channel in channels if channel.id is not None and channel.short_name in PUBLIC_BROADCASTERS]
        other_ids = [channel.id for channel in channels if channel.id is not None and channel.short_name not in PUBLIC_BROADCASTERS]
        self.repository.create('Öffentlich-rechtlich', public_ids)
        self.repository.create('Nachrichten & International', other_ids)

    def list_groups_with_channels(self) -> list[tuple[ChannelGroup, list[Channel]]]:
        return [(group, self.repository.list_channels(group.id)) for group in self.repository.list_groups() if group.id is not None]

    def create(self, name: str, channel_ids: list[int]) -> None:
        self.repository.create(name, channel_ids)

    def member_ids(self, group_id: int) -> list[int]:
        return self.repository.member_ids(group_id)

    def replace_members(self, group_id: int, channel_ids: list[int]) -> None:
        self.repository.replace_members(group_id, channel_ids)

    def rename(self, group_id: int, name: str) -> None:
        self.repository.rename(group_id, name)

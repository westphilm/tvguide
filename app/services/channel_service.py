from __future__ import annotations

from app.db.channel_repository import ChannelRepository
from app.config.channel_catalog import CHANNEL_CATALOG
from app.models.channel import Channel


class ChannelService:
    def __init__(self, repository: ChannelRepository) -> None:
        self.repository = repository

    def ensure_defaults(self) -> None:
        existing_short_names = {channel.short_name for channel in self.repository.list_all()}
        for index, catalog_channel in enumerate(CHANNEL_CATALOG):
            if catalog_channel.short_name in existing_short_names:
                continue
            self.repository.insert(
                Channel(
                    id=None,
                    name=catalog_channel.name,
                    short_name=catalog_channel.short_name,
                    sort_index=index,
                    enabled=True,
                )
            )

    def list_enabled(self) -> list[Channel]:
        return self.repository.list_enabled()

    def move(self, channel_id: int, offset: int) -> None:
        channels = self.repository.list_enabled()
        current_index = next(
            (index for index, channel in enumerate(channels) if channel.id == channel_id),
            None,
        )
        if current_index is None:
            return

        target_index = current_index + offset
        if target_index < 0 or target_index >= len(channels):
            return

        channels[current_index], channels[target_index] = (
            channels[target_index],
            channels[current_index],
        )
        self.repository.update_sort_order(channels)

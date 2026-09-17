from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.db.channel_repository import ChannelRepository
from app.db.channel_group_repository import ChannelGroupRepository
from app.db.database import Database
from app.db.program_repository import ProgramRepository
from app.models.channel import Channel
from app.models.program_item import ProgramItem
from app.providers.base import ProgramProvider
from app.services.channel_service import ChannelService
from app.services.channel_group_service import ChannelGroupService
from app.services.program_service import ProgramService


class FixedProvider(ProgramProvider):
    def __init__(self) -> None:
        self.calls = 0

    def get_program(self, channel: Channel, now: datetime) -> list[ProgramItem]:
        self.calls += 1
        assert channel.id is not None
        return [
            ProgramItem(None, channel.id, 'current', 'Current', now - timedelta(minutes=5), now + timedelta(minutes=25)),
            ProgramItem(None, channel.id, 'next', 'Next', now + timedelta(minutes=25), now + timedelta(minutes=55)),
            ProgramItem(None, channel.id, 'following', 'Following', now + timedelta(minutes=55), now + timedelta(minutes=85)),
        ]


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / 'test.db')
        self.database.initialize()
        self.channel_repository = ChannelRepository(self.database)
        self.channel_service = ChannelService(self.channel_repository)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_channel_order_is_persistent(self) -> None:
        first = self.channel_repository.insert(Channel(None, 'One', 'ONE', 0))
        second = self.channel_repository.insert(Channel(None, 'Two', 'TWO', 1))

        self.channel_service.move(second.id, -1)

        channels = self.channel_repository.list_enabled()
        self.assertEqual(['TWO', 'ONE'], [channel.short_name for channel in channels])
        self.assertEqual([0, 1], [channel.sort_index for channel in channels])

    def test_program_overview_contains_current_and_next(self) -> None:
        channel = self.channel_repository.insert(Channel(None, 'One', 'ONE', 0))
        now = datetime(2026, 9, 16, 20, 15)
        program_service = ProgramService(ProgramRepository(self.database), FixedProvider())

        program_service.refresh([channel], now)
        overviews = program_service.build_overviews([channel], now)

        self.assertEqual('Current', overviews[0].current_program.title)
        self.assertEqual('Next', overviews[0].next_program.title)
        self.assertEqual('Following', overviews[0].following_program.title)

    def test_programs_are_refreshed_once_per_day_across_service_instances(self) -> None:
        channel = self.channel_repository.insert(Channel(None, 'One', 'ONE', 0))
        now = datetime(2026, 9, 16, 20, 15)
        first_provider = FixedProvider()

        ProgramService(ProgramRepository(self.database), first_provider).refresh([channel], now)

        second_provider = FixedProvider()
        ProgramService(ProgramRepository(self.database), second_provider).refresh(
            [channel], now + timedelta(minutes=30)
        )

        self.assertEqual(1, first_provider.calls)
        self.assertEqual(0, second_provider.calls)

    def test_channel_groups_keep_the_selected_channels(self) -> None:
        first = self.channel_repository.insert(Channel(None, 'One', 'ONE', 0))
        second = self.channel_repository.insert(Channel(None, 'Two', 'TWO', 1))
        group_service = ChannelGroupService(ChannelGroupRepository(self.database))

        group_service.create('Favoriten', [second.id])

        groups = group_service.list_groups_with_channels()
        self.assertEqual('Favoriten', groups[0][0].name)
        self.assertEqual(['TWO'], [channel.short_name for channel in groups[0][1]])


if __name__ == '__main__':
    unittest.main()

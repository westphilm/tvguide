import os
from pathlib import Path

from nicegui import ui

from app.db.channel_repository import ChannelRepository
from app.db.channel_group_repository import ChannelGroupRepository
from app.db.database import Database
from app.db.program_repository import ProgramRepository
from app.providers.xmltv_provider import XmltvProgramProvider
from app.services.channel_service import ChannelService
from app.services.channel_group_service import ChannelGroupService
from app.services.program_service import ProgramService
from app.ui.pages.television import register_television_page


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'tvguide.db'
EPG_CACHE_PATH = DATA_DIR / 'epg' / 'germany.xml.gz'
DEFAULT_EPG_URL = 'https://www.open-epg.com/files/germany.xml.gz'
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9000


def create_app() -> tuple[ChannelService, ChannelGroupService, ProgramService]:
    database = Database(DB_PATH)
    database.initialize()

    channel_service = ChannelService(ChannelRepository(database))
    channel_service.ensure_defaults()
    channel_group_service = ChannelGroupService(ChannelGroupRepository(database))
    channel_group_service.ensure_defaults(channel_service.list_enabled())

    feed_url = os.environ.get('TVGUIDE_EPG_URL', DEFAULT_EPG_URL)
    provider = XmltvProgramProvider(feed_url, feed_cache_path=EPG_CACHE_PATH)

    program_service = ProgramService(
        repository=ProgramRepository(database),
        provider=provider,
    )

    return channel_service, channel_group_service, program_service


channel_service, channel_group_service, program_service = create_app()
register_television_page(channel_service, channel_group_service, program_service)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        host=os.environ.get('TVGUIDE_HOST', DEFAULT_HOST),
        port=int(os.environ.get('TVGUIDE_PORT', DEFAULT_PORT)),
        title='tvguide',
        reload=False,
        show=False,
    )

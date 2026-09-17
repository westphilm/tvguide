from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
import gzip
from io import BytesIO
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from app.config.channel_catalog import CHANNEL_XMLTV_IDS
from app.models.channel import Channel
from app.models.program_item import ProgramItem
from app.providers.base import ProgramProvider


class XmltvProgramProvider(ProgramProvider):
    def __init__(
        self,
        feed_url: str,
        channel_ids: dict[str, str] | None = None,
        cache_ttl: timedelta = timedelta(minutes=15),
        feed_cache_path: str | Path | None = None,
        downloader: Callable[[str], bytes] | None = None,
    ) -> None:
        self.feed_url = feed_url
        self.channel_ids = channel_ids or CHANNEL_XMLTV_IDS
        self.cache_ttl = cache_ttl
        self.feed_cache_path = Path(feed_cache_path) if feed_cache_path else None
        self.downloader = downloader or self._download
        self._cached_at: datetime | None = None
        self._programs_by_source_id: dict[str, list[ProgramItem]] = {}

    def get_program(self, channel: Channel, now: datetime) -> list[ProgramItem]:
        if channel.id is None:
            raise ValueError('Channel must be persisted')

        self._refresh_cache_if_needed(now)
        source_id = self.channel_ids.get(channel.short_name.upper())
        if source_id is None:
            return []

        return [
            replace(item, channel_id=channel.id)
            for item in self._programs_by_source_id.get(source_id, [])
        ]

    def _refresh_cache_if_needed(self, now: datetime) -> None:
        if self._cached_at and now - self._cached_at < self.cache_ttl:
            return

        content = self.downloader(self.feed_url)
        self._store_feed_cache(content)
        self._programs_by_source_id = self._parse(content)
        self._cached_at = now

    def _store_feed_cache(self, content: bytes) -> None:
        if self.feed_cache_path is None:
            return

        self.feed_cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.feed_cache_path.with_suffix(
            f'{self.feed_cache_path.suffix}.tmp'
        )
        temporary_path.write_bytes(content)
        temporary_path.replace(self.feed_cache_path)

    def _parse(self, content: bytes) -> dict[str, list[ProgramItem]]:
        if content.startswith(b'\x1f\x8b'):
            content = gzip.decompress(content)

        source_ids = set(self.channel_ids.values())
        programs_by_source_id = {source_id: [] for source_id in source_ids}

        for _, element in ElementTree.iterparse(BytesIO(content), events=('end',)):
            if element.tag != 'programme':
                continue

            source_id = element.get('channel')
            if source_id in source_ids:
                title = element.findtext('title')
                start_at = self._parse_datetime(element.get('start'))
                end_at = self._parse_datetime(element.get('stop'))
                if title and start_at and end_at:
                    programs_by_source_id[source_id].append(
                        ProgramItem(
                            id=None,
                            channel_id=0,
                            external_id=f'xmltv:{source_id}:{element.get("start")}',
                            title=title,
                            start_at=start_at,
                            end_at=end_at,
                            category=element.findtext('category'),
                            description=element.findtext('desc'),
                            subtitle=element.findtext('sub-title'),
                        )
                    )
            element.clear()

        return programs_by_source_id

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.strptime(value, '%Y%m%d%H%M%S %z')
        except ValueError:
            try:
                return datetime.strptime(value[:14], '%Y%m%d%H%M%S')
            except ValueError:
                return None
        return parsed.astimezone().replace(tzinfo=None)

    @staticmethod
    def _download(feed_url: str) -> bytes:
        request = Request(feed_url, headers={'User-Agent': 'Television/0.1'})
        with urlopen(request, timeout=20) as response:
            return response.read()

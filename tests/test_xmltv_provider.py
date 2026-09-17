from datetime import datetime, timedelta
import gzip
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.models.channel import Channel
from app.providers.xmltv_provider import XmltvProgramProvider


FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'sample.xml'


class XmltvProgramProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.content = FIXTURE_PATH.read_bytes()
        self.channel = Channel(1, 'Das Erste', 'ARD', 0)
        self.now = datetime(2026, 9, 16, 20, 15)

    def test_returns_mapped_programs_with_metadata(self) -> None:
        provider = XmltvProgramProvider(
            'https://example.test/guide.xml',
            downloader=lambda _: self.content,
        )

        programs = provider.get_program(self.channel, self.now)

        self.assertEqual(['Tagesschau', 'Reportage'], [program.title for program in programs])
        self.assertEqual('Nachrichten', programs[0].category)
        self.assertEqual('Die wichtigsten Nachrichten', programs[0].subtitle)
        self.assertEqual('Die Nachrichten des Tages.', programs[0].description)
        self.assertEqual(1, programs[0].channel_id)

    def test_accepts_gzip_content_and_caches_downloads(self) -> None:
        calls = 0

        def download(_: str) -> bytes:
            nonlocal calls
            calls += 1
            return gzip.compress(self.content)

        provider = XmltvProgramProvider(
            'https://example.test/guide.xml.gz',
            cache_ttl=timedelta(minutes=15),
            downloader=download,
        )

        provider.get_program(self.channel, self.now)
        provider.get_program(self.channel, self.now + timedelta(minutes=5))

        self.assertEqual(1, calls)

    def test_stores_the_downloaded_feed_locally(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            cache_path = Path(temporary_directory) / 'epg' / 'germany.xml.gz'
            compressed_content = gzip.compress(self.content)
            provider = XmltvProgramProvider(
                'https://example.test/guide.xml.gz',
                feed_cache_path=cache_path,
                downloader=lambda _: compressed_content,
            )

            provider.get_program(self.channel, self.now)

            self.assertEqual(compressed_content, cache_path.read_bytes())


if __name__ == '__main__':
    unittest.main()

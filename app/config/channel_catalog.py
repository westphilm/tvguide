from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CatalogChannel:
    name: str
    short_name: str
    xmltv_id: str
    logo_url: str
    stream_url: str


def _channel(name: str, short_name: str, xmltv_id: str, logo_id: str, stream_url: str) -> CatalogChannel:
    return CatalogChannel(name, short_name, xmltv_id, f'https://images.open-epg.com/{logo_id}.png', stream_url)


CHANNEL_CATALOG = [
    _channel('Das Erste', 'ARD', 'DasErste.de', 'x250', 'https://www.ardmediathek.de/live'),
    _channel('ZDF', 'ZDF', 'ZDF.de', 'x446', 'https://www.zdf.de/live-tv'),
    _channel('ZDFinfo', 'ZDFINFO', 'ZDFinfo.de', 'x332', 'https://www.zdf.de/live-tv'),
    _channel('ZDFneo', 'ZDFNEO', 'ZDFneo.de', 'x333', 'https://www.zdf.de/live-tv'),
    _channel('arte', 'ARTE', 'ARTE.de', 'x239', 'https://www.arte.tv/de/live/'),
    _channel('3sat', '3SAT', '3sat.de', 'x238', 'https://www.3sat.de/live/index.html'),
    _channel('phoenix', 'PHOENIX', 'phoenix.de', '8010', 'https://www.phoenix.de/live'),
    _channel('ONE', 'ONE', 'ONE.de', '8006', 'https://www.ardmediathek.de/live'),
    _channel('ARD alpha', 'ARD_ALPHA', 'ARDalpha.de', 'x240', 'https://www.ardmediathek.de/live'),
    _channel('BR Fernsehen Süd', 'BR', 'BRFernsehenSued.de', '7905', 'https://www.ardmediathek.de/live'),
    _channel('hr-fernsehen', 'HR', 'hrfernsehen.de', '7948', 'https://www.ardmediathek.de/live'),
    _channel('MDR Sachsen', 'MDR', 'MDRSachsen.de', '7973', 'https://www.ardmediathek.de/live'),
    _channel('NDR Niedersachsen', 'NDR', 'NDRNiedersachsen.de', '7987', 'https://www.ardmediathek.de/live'),
    _channel('rbb Fernsehen Berlin', 'RBB', 'rbbFernsehenBerlin.de', '8020', 'https://www.ardmediathek.de/live'),
    _channel('SR Fernsehen', 'SR', 'SRFernsehen.de', '8105', 'https://www.ardmediathek.de/live'),
    _channel('SWR Baden-Württemberg', 'SWR', 'SWRBadenWuerttemberg.de', '8112', 'https://www.ardmediathek.de/live'),
    _channel('WDR Fernsehen', 'WDR', 'WDRFernsehen.de', 'nologo', 'https://www.ardmediathek.de/live'),
    _channel('n-tv', 'NTV', 'ntv.de', 'x331', 'https://www.n-tv.de/mediathek/livestream/'),
    _channel('WELT', 'WELT', 'WELT.de', 'x324', 'https://www.welt.de/mediathek/live'),
    _channel('BBC News', 'BBC_NEWS', 'BBCNews.de', '7896', 'https://www.bbc.com/news/live'),
    _channel('CNN International', 'CNN', 'CNNInternational.de', '7911', 'https://edition.cnn.com/tv/live'),
]

CATALOG_BY_SHORT_NAME = {channel.short_name: channel for channel in CHANNEL_CATALOG}
CHANNEL_XMLTV_IDS = {channel.short_name: channel.xmltv_id for channel in CHANNEL_CATALOG}
PUBLIC_BROADCASTERS = {'ARD', 'ZDF', 'ZDFINFO', 'ZDFNEO', 'ARTE', '3SAT', 'PHOENIX', 'ONE', 'ARD_ALPHA', 'BR', 'HR', 'MDR', 'NDR', 'RBB', 'SR', 'SWR', 'WDR'}

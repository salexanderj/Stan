import yt_dlp
import asyncio

from voice.download_type import DownloadType
from voice.media_info import MediaInfo

yt_dlp.utils.bug_reports_message = lambda: ''


class Downloader(yt_dlp.YoutubeDL):

    def __init__(self, download_type: DownloadType):
        options = {
            'format': download_type,
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'verbose': True,
            'no_warnings': True,
            'default_search': 'auto',
            'cookiefile': 'cookies.txt',
            'cachedir': False
        }

        super().__init__(options)

    async def extract_media_info(self, url: str) -> [MediaInfo]:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self.extract_info(url, download=False))

        infos = []

        if "entries" in data:
            for entry in data["entries"]:
                info = MediaInfo(entry["title"],
                                 entry["webpage_url"],
                                 entry["url"],
                                 entry["ext"],
                                 entry["extractor"],
                                 entry["thumbnail"] if "thumbnail" in entry else None)
                infos.append(info)
            return infos

        info = MediaInfo(data["title"],
                         data["webpage_url"],
                         data["url"],
                         data["ext"],
                         data["extractor"],
                         data["thumbnail"] if "thumbnail" in data else None)
        infos.append(info)
        return infos


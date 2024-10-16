import yt_dlp
import asyncio
from typing import List, Optional
from abc import ABC, abstractmethod

from downloads.media_type import MediaType
from downloads.media_info import MediaInfo

yt_dlp.utils.bug_reports_message = lambda: ''


class Downloader(yt_dlp.YoutubeDL, ABC):

    def __init__(self, media_type: MediaType):

        self.media_type = media_type
        options = self.get_options(media_type)
        super().__init__(options)

    @abstractmethod
    def get_options(self, media_type: MediaType):
        pass

    async def extract_media_info(self,
                                 url: str,
                                 requester_name: Optional[str] = None,
                                 requester_avatar_url: Optional[str] = None) -> List[MediaInfo]:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self.extract_info(url, download=False))

        infos = []

        if 'entries' in data:
            for entry in data['entries']:
                info = MediaInfo(entry['title'],
                                 entry['webpage_url'],
                                 entry['url'],
                                 entry['ext'],
                                 entry['extractor'],
                                 entry['thumbnail'] if 'thumbnail' in entry else None,
                                 self.media_type,
                                 requester_name=requester_name,
                                 requester_avatar_url=requester_avatar_url)
                infos.append(info)
            return infos

        info = MediaInfo(data['title'],
                         data['webpage_url'],
                         data['url'],
                         data['ext'],
                         data['extractor'],
                         data['thumbnail'] if 'thumbnail' in data else None,
                         self.media_type,
                         requester_name=requester_name,
                         requester_avatar_url=requester_avatar_url)
        infos.append(info)
        return infos

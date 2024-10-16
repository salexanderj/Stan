from dataclasses import dataclass
from typing import Optional

from downloads.media_type import MediaType


@dataclass
class MediaInfo:
    title: str
    page_url: str
    media_url: str
    extension: str
    extractor: str
    thumbnail: Optional[str]
    media_type: MediaType
    requester_name: Optional[str]
    requester_avatar_url: Optional[str]

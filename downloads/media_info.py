from dataclasses import dataclass
from typing import Optional


@dataclass
class MediaInfo:
    title: str
    page_url: str
    media_url: str
    extension: str
    extractor: str
    thumbnail: Optional[str]

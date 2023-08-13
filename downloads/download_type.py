from enum import Enum


class DownloadType(Enum):
    VIDEO = 'b'
    AUDIO = 'ba'
    RADIO = 'ba*'
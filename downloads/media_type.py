from enum import Enum


class MediaType(Enum):
    VIDEO = 'b'
    AUDIO = 'ba'
    RADIO = 'ba*'

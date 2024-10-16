from enum import Enum


class MediaType(Enum):
    VIDEO = 'b*'
    VIDEO_ONLY = 'b'
    AUDIO = 'ba*'
    AUDIO_ONLY = 'ba'

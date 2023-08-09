import disnake
from voice.media_info import MediaInfo


class Song:

    def __init__(self, media_info: MediaInfo, owner: disnake.Member):

        self.media_info = media_info
        self.name = media_info.title
        self.owner = owner

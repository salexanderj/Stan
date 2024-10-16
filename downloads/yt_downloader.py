from downloads.downloader import Downloader
from downloads.media_type import MediaType


class YTDownloader(Downloader):

    def get_options(self, media_type: MediaType):

        options_youtube = {
            'format': media_type.value,
            # 'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'outtmpl': '-',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'verbose': True,
            'no_warnings': True,
            'default_search': 'auto',
            'username': 'oauth2',
            'password': ''
        }

        return options_youtube

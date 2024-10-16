from downloads.downloader import Downloader
from downloads.media_type import MediaType


class OtherDownloader(Downloader):

    def get_options(self, media_type: MediaType):

        options_other = {
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
        }

        return options_other

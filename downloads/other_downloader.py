from downloads.downloader import Downloader
from downloads.download_type import DownloadType
    
class OtherDownloader(Downloader):
     
    def get_options(self, download_type: DownloadType):

        options_other = {
            'format': download_type.value,
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

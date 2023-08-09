import yt_dlp
import asyncio

from voice.media_info import MediaInfo

yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'verbose': True,
    'no_warnings': True,
    'default_search': 'auto',
    'cookiefile': 'cookies.txt',
    'cachedir': False
}


ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


async def extract_media_info(url: str) -> [MediaInfo]:

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

    infos = []

    if "entries" in data:
        for entry in data["entries"]:
            info = MediaInfo(entry["title"],
                             entry["webpage_url"],
                             entry["url"],
                             entry["ext"],
                             entry["extractor"],
                             entry["thumbnail"] if "thumbnail" in entry else None)
            infos.append(info)
        return infos

    info = MediaInfo(data["title"],
                     data["webpage_url"],
                     data["url"],
                     data["ext"],
                     data["extractor"],
                     data["thumbnail"] if "thumbnail" in data else None)
    infos.append(info)
    return infos


def get_ffmpeg_options(speed: float = 1) -> dict[str, str]:
    speed = round(speed, 2)

    if speed < 0.01:
        speed = 0.01
    elif speed > 10:
        speed = 10

    ffmpeg_options = {
        'options': f'-vn -filter:a "atempo={speed},atempo={speed}"',
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

    return ffmpeg_options


# async def download_media(url: str, media_type: MediaType) -> io.BytesIO:
#
#     ext_loops = asyncio.get_event_loop()
#     if media_type is MediaType.Audio:
#         data = await ext_loops.run_in_executor(None, lambda: ytdl_audio.download())
#     else:
#         data = await ext_loops.run_in_executor(None, lambda: ytdl_video.extract_info(url, download=False))

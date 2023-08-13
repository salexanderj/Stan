import asyncio
import io
from contextlib import redirect_stdout

import disnake
from disnake.ext import commands

from bot import Stan
from downloads.downloader import Downloader
from downloads.download_type import DownloadType


class Ripper(commands.Cog):

    def __init__(self, bot: Stan):
        self.bot = bot

    @commands.slash_command(
        description="Stan will try to rip an audio file from the specified url.",
        dm_permission=True
    )
    async def rip_audio(self,
                        inter: disnake.ApplicationCommandInteraction,
                        url: str,
                        ) -> None:

        await inter.response.defer()

        loop = asyncio.get_event_loop()
        downloader = Downloader(download_type=DownloadType.AUDIO)
        infos = await downloader.extract_media_info(url)
        info = infos[0]

        buffer = io.BytesIO()
        buffer_close = buffer.close
        buffer.close = lambda *_: ...
        with redirect_stdout(buffer):
            await loop.run_in_executor(None, lambda: downloader.download(url))

        buffer.seek(0)
        file = disnake.File(buffer,
                            filename=f"{info.title}.{'mp3' if info.extension == 'webm' or 'mp4' else info.extension}")

        await inter.send(file=file)
        buffer_close()


def setup(bot: Stan):
    bot.add_cog(Ripper(bot))

import disnake
import lavalink
from datetime import datetime
from typing import Optional

import utils
from downloads.media_info import MediaInfo


class StanPlayer(lavalink.DefaultPlayer):

    def __init__(self, guild_id: int, node: lavalink.Node) -> None:
        super().__init__(guild_id, node)

        self._embed_message: Optional[disnake.Message] = None

    async def send_or_update_embed_message(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if not self._embed_message:
            self._embed_message = await self._send_embed_message(inter)
            return
        elif self._embed_message.channel is not inter.channel and inter.permissions.send_messages:
            await self._embed_message.delete()
            self._embed_message = await self._send_embed_message()
            return

        await self._update_embed_message()

    async def try_update_embed_message(self) -> bool:
        if not self._embed_message:
            return False
        await self._update_embed_message()

    async def clear_embed_message(self):
        if self._embed_message:
            await self._embed_message.delete()
            self._embed_message = None

    async def _send_embed_message(self, inter: disnake.ApplicationCommandInteraction) -> disnake.Message:
        embed = self._generate_embed()
        message = await inter.channel.send(embed=embed)
        return message

    async def _update_embed_message(self) -> None:
        new_embed = self._generate_embed()
        await self._embed_message.edit(embeds=[new_embed])

    def _generate_embed(self) -> disnake.Embed:

        embed = disnake.Embed(
                title='Echoes of the Void',
                color=0x8c041f,
                timestamp=datetime.now())

        songs_field = ''
        requesters_field = ''
        links_field = ''

        current = self.current
        current_media_info: MediaInfo = current.extra['media_info']
        if current is not None:
            requester_name = current_media_info.requester_name
            requester_avatar_url = current_media_info.requester_avatar_url
            embed.set_author(
                    name=requester_name,
                    icon_url=requester_avatar_url)

            if current_media_info.thumbnail:
                embed.set_thumbnail(current_media_info.thumbnail)

            songs_field += f":arrow_forward: {utils.trim(current_media_info.title, 25)}\n"
            requesters_field += f"{utils.trim(requester_name, 9)}\n"
            links_field += f"[{current_media_info.extractor}]({current_media_info.page_url})\n"

        tracks = self.queue
        if len(tracks) > 0:
            count = 0
            for idx, i in enumerate(tracks):
                if count == 25:
                    break
                media_info: MediaInfo = i.extra['media_info']
                requester_name = media_info.requester_name
                requester_avatar_url = media_info.requester_avatar_url
                songs_field += f"{idx + 1}. {utils.trim(media_info.title, 25)}\n"
                requesters_field += f"{utils.trim(requester_name, 9)}\n"
                links_field += f"[{media_info.extractor}]({media_info.page_url})\n"
                count += 1

        embed.add_field("Queue", songs_field)
        embed.add_field("Requester", requesters_field)
        embed.add_field("Source", links_field)

        embed.set_footer(text=f"Currently looping:  {self.loop == 2}")

        return embed

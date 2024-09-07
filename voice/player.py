import disnake
import lavalink
from datetime import datetime
from typing import Optional

import utils

class StanPlayer(lavalink.DefaultPlayer):

    def __init__(self, guild_id: int, node: lavalink.Node) -> None:
        super().__init__(guild_id, node)

        self._embed_message: Optional[disnake.Message] = None

    async def send_embed(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if not self._embed_message:
            embed = self.generate_embed()
            await inter.send(embed=embed)
            self._embed_message = await inter.original_response()
            return

        if (
            self._embed_message.channel is not inter.channel
            and inter.permissions.send_messages
        ):
            await self._embed_message.delte()     
            embed = self.generate_embed()
            await inter.send(embed=embed)
            self._embed_message = await inter.original_response()
            return

        new_embed = self.generate_embed()
        await self._embed_message.edit(embeds=[new_embed])
        await inter.delete_original_message()

    async def clear_embed(self):
        if self._embed_message:
            await self._embed_message.delete()
            self._embed_message = None

    def generate_embed(self) -> disnake.Embed:

        embed = disnake.Embed(
                title='Echoes of the Void',
                color=0x8c041f,
                timestamp=datetime.now()) 

        songs_field = ''
        requesters_field = ''
        links_field = ''

        current = self.current
        if current is not None:
            requester_name = current.extra['requester_name']
            requester_avatar_url = current.extra['requester_avatar_url']
            embed.set_author(
                    name=requester_name,
                    icon_url=requester_avatar_url)

            if current.artwork_url:
                embed.set_thumbnail(current.artwork_url)

            songs_field += f":arrow_forward: {utils.trim(current.title, 25)}\n"
            requesters_field += f"{utils.trim(requester_name, 9)}\n"
            links_field += f"[{current.isrc or current.source_name}]({current.uri})\n"

        tracks = self.queue    
        if len(tracks) > 0:
            count = 0
            for idx, i in enumerate(tracks):
                if count == 25:
                    break
                requester_name = i.extra['requester_name']
                requester_avatar_url = i.extra['requester_avatar_url']
                songs_field += f"{idx + 1}. {utils.trim(i.title, 25)}\n"
                requesters_field += f"{utils.trim(requester_name, 9)}\n"
                links_field += f"[{i.isrc or i.source_name}]({i.uri})\n"
                count += 1    

        embed.add_field("Queue", songs_field)
        embed.add_field("Requester", requesters_field)
        embed.add_field("Source", links_field)

        embed.set_footer(text=f"Currently looping:  {self.loop == 2}")

        return embed

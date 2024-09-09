import disnake
from disnake.ext import commands
import lavalink
from lavalink.events import TrackStartEvent, QueueEndEvent
from lavalink.errors import ClientError
from lavalink.filters import LowPass
from lavalink.server import LoadType
import re

from bot import Stan
from voice.player import StanPlayer
from voice.helpers import create_player, attach_track_metadata
from config import LAVALINK_PASSWORD

url_rx = re.compile(r'https?://(?:www\.)?.+')


class Bard(commands.Cog):
    def __init__(self, bot: Stan):
        self.bot = bot

        if not hasattr(self.bot, 'lavalink'):
            self.bot.lavalink = lavalink.Client(
                    self.bot.user.id,
                    player=StanPlayer)
            self.bot.lavalink.add_node(host='localhost',
                                       port=2333,
                                       password=LAVALINK_PASSWORD,
                                       region='us',
                                       name='default-node')
        self.bot.lavalink.add_event_hooks(self)

    def cog_unload(self) -> None:
        self.bot.lavalink._event_hooks.clear()

    async def cog_slash_command_error(self,
                                      inter: disnake.ApplicationCommandInteraction,
                                      error: Exception) -> None:
        if isinstance(error, commands.CommandInvokeError):
            await inter.send(error.original, delete_after=8)
        raise error

    @lavalink.listener(TrackStartEvent)
    async def on_track_start(self, event: TrackStartEvent):
        guild_id = event.player.guild_id
        guild = self.bot.get_guild(guild_id)

        if not guild:
            return await self.lavalink.player_manager.destroy(guild_id)

        await event.player.try_update_embed_message()

    @lavalink.listener(QueueEndEvent)
    async def on_queue_end(self, event: QueueEndEvent):
        guild_id = event.player.guild_id
        guild = self.bot.get_guild(guild_id)

        if guild is not None:
            await guild.voice_client.disconnect(force=True)

        await event.player.clear_embed_message()

    @commands.slash_command(
        description="Command Stan to play audio from a url.",
        dm_permission=False
    )
    async def play(self,
                   inter: disnake.ApplicationCommandInteraction,
                   query: str = commands.Param(description="The url to play.")
                   ) -> None:
        player = await create_player(inter, True)

        await inter.response.defer()

        query = query.strip('<>')
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if results.load_type == LoadType.EMPTY:
            return await inter.send('I couldn\'t find any tracks for that query.')
        elif results.load_type == LoadType.PLAYLIST:
            tracks = results.tracks
            for track in tracks:
                track_with_metadata = attach_track_metadata(track, inter)
                player.add(track=track_with_metadata, requester=inter.author.id)
        else:
            track = results.tracks[0]
            track_with_metadata = attach_track_metadata(track, inter)
            player.add(track=track_with_metadata, requester=inter.author.id)

        if not player.is_playing:
            await player.play()

        await player.send_or_update_embed_message(inter)
        await inter.delete_original_response()

    @commands.slash_command(
        description="Command Stan to skip the current item in queue.",
        dm_permission=False
    )
    async def skip(self,
                   inter: disnake.ApplicationCommandInteraction
                   ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        skipped_track_title = player.current.title if player.current else None
        message = f'Skipping {skipped_track_title}...' if skipped_track_title else 'Skipping...'
        await player.skip()
        await player.send_or_update_embed_message(inter)
        await inter.send(message, delete_after=6)

    @commands.slash_command(
        description="Forces Stan to disconnect from the voice channel in this guild.",
        dm_permission=False
    )
    async def disconnect(self,
                         inter: disnake.ApplicationCommandInteraction
                         ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        player.queue.clear()
        await player.clear_embed_message()
        await player.stop()

        voice_channel_name = inter.guild.voice_client.channel.name
        await inter.guild.voice_client.disconnect(force=True)
        await inter.send(f'Banished from {voice_channel_name}...', delete_after=4)

    @commands.slash_command(
        description="Command Stan to toggle looping queue mode.",
        dm_permission=False
    )
    async def loop(self,
                   inter: disnake.ApplicationCommandInteraction
                   ):
        player = await create_player(inter, False)
        await inter.response.defer()

        if player.loop == 0:
            player.set_loop(2)
            await player.send_or_update_embed_message(inter)
            await inter.send('Looping enabled...', delete_after=4)
        else:
            player.set_loop(0)
            await player.send_embed(inter)
            await inter.send('Looping disabled...', delete_after=4)


def setup(bot: Stan) -> None:
    bot.add_cog(Bard(bot))

import disnake
from disnake.ext import commands
import lavalink
from lavalink.events import TrackStartEvent, QueueEndEvent
from typing import Optional

from bot import Stan
from config import LAVALINK_PASSWORD
from voice.player import StanPlayer
from voice.helpers import create_player
from downloads.helpers import extract_tracks


class Bard(commands.Cog):
    def __init__(self, bot: Stan):
        self.bot = bot

        if not hasattr(self.bot, 'lavalink'):
            self.register_lavalink()
        self.bot.lavalink.add_event_hooks(self)

    def register_lavalink(self):
        self.bot.lavalink = lavalink.Client(
                self.bot.user.id,
                player=StanPlayer)
        self.bot.lavalink.add_node(host='localhost',
                                   port=2333,
                                   password=LAVALINK_PASSWORD,
                                   region='us',
                                   name='default-node')

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
                   query: str = commands.Param(description="The url to play."),
                   deferred_start: bool = commands.Param(
                       description="Defers playback start until Stan is manually started using '/resume'.",
                       default=False
                       )
                   ) -> None:
        player = await create_player(inter, True)

        await inter.response.defer()

        tracks = await extract_tracks(query,
                                      player,
                                      inter.author.display_name,
                                      inter.author.display_avatar.url)

        if len(tracks) < 1:
            await inter.send("I couldn't find any tracks for that query.", delete_after=6)
            return

        for track in tracks:
            player.add(track, inter.author.id)

        if not player.is_playing and not deferred_start:
            await player.play()

        await player.send_or_update_embed_message(inter)
        await inter.delete_original_response()

    @commands.message_command(
            name="play selected",
            description="Command Stan to play audio from embeds or files in the selected message.",
            dm_permission=False
            )
    async def play_selected(self,
                            inter: disnake.ApplicationCommandInteraction,
                            ) -> None:
        await inter.response.defer()

        message = inter.target

        urls = []
        for attachment in message.attachments:
            if "video" in attachment.content_type or "audio" in attachment.content_type:
                urls.append(attachment.url)
        for embed in message.embeds:
            if embed.video.url is not None:
                urls.append(embed.video.url)

        if len(urls) < 1:
            await inter.send("No media found in the selected message.", delete_after=6)
            return

        player = await create_player(inter, True)

        for url in urls:
            tracks = await extract_tracks(url,
                                          player,
                                          inter.author.display_name,
                                          inter.author.display_avatar.url)

        for track in tracks:
            player.add(track, inter.author.id)

        if not player.is_playing:
            await player.play()

        await player.send_or_update_embed_message(inter)
        await inter.delete_original_response()

    @commands.slash_command(
        description="Command Stan to pause playback.",
        dm_permission=False
    )
    async def pause(self,
                    inter: disnake.ApplicationCommandInteraction
                    ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        if not player.is_playing:
            await inter.send("Nothing to pause.", delete_after=4)
            return
        if player.paused:
            await inter.send("Already paused.", delete_after=4)
            return

        await player.set_pause(True)
        await inter.send("Pausing...", delete_after=6)

    @commands.slash_command(
        description="Command Stan to resume playback.",
        dm_permission=False
    )
    async def resume(self,
                     inter: disnake.ApplicationCommandInteraction
                     ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        if not player.paused and player.is_playing:
            await inter.send("Already playing.", delete_after=4)
            return
        elif not player.paused and not player.is_playing:
            await player.play()
            await inter.send("Forcing player to play...", delete_after=6)
            return
        await player.set_pause(False)
        await inter.send("Resuming...", delete_after=6)

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
                   ) -> None:
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

    @commands.slash_command(
            dm_permission=False
            )
    async def filter(self,
                     inter: disnake.ApplicationCommandInteraction
                     ) -> None:
        pass

    @filter.sub_command(
            description="Sets the playback rate of the current player."
            )
    async def rate(self,
                   inter: disnake.ApplicationCommandInteraction,
                   rate: float = commands.Param(
                        le=10.0,
                        ge=0.1,
                        description="Rate of playback."),
                   ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        existing_filter = player.get_filter('timescale')
        existing_pitch: Optional[float] = None
        if existing_filter:
            existing_pitch = existing_filter.values['pitch']

        await player.update_filter(lavalink.filters.Timescale, rate=rate)

        message = f"Applying timescale filter with rate multiplier set to {rate}x"
        if existing_filter:
            message += f", carrying over existing pitch multiplier of {existing_pitch}x..."
        else:
            message += "..."
        await inter.send(message, delete_after=8)

    @filter.sub_command(
            description="Sets the playback rate of the current player."
            )
    async def pitch(self,
                    inter: disnake.ApplicationCommandInteraction,
                    pitch: float = commands.Param(
                        le=10.0,
                        ge=0.1,
                        description="Pitch of playback."),
                    ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        existing_filter = player.get_filter('timescale')
        existing_rate: Optional[float] = None
        if existing_filter:
            existing_rate = existing_filter.values['rate']

        await player.update_filter(lavalink.filters.Timescale, pitch=pitch)

        message = f"Applying timescale filter with pitch set to {pitch}x"
        if existing_filter:
            message += f", carrying over existing rate multiplier of {existing_rate}x..."
        else:
            message += "..."
        await inter.send(message, delete_after=8)

    @filter.sub_command(
            description="Applies a distortion effect to the current player."
            )
    async def distortion(self,
                         inter: disnake.ApplicationCommandInteraction,
                         option: int = commands.Param(
                             description="The distortion setting to be used.",
                             choices={
                                 'Light': 0,
                                 'Medium': 1,
                                 'Heavy': 2,
                                 'Extreme (Loud)': 3
                                 }
                             )
                         ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        options = {
                0: [0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.5, 1.0],
                1: [0.5, 1.0, 0.5, 1.0, 0.1, 1.7, 0.5, 1.0],
                2: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.1, 1.0],
                3: [1.0, 10.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.25]
        }

        filter = lavalink.filters.Distortion(*options[option])
        await player.set_filter(filter)

        await inter.send("Applying distortion filter...", delete_after=8)

    @filter.sub_command(
            description="Phases the audio between the right and left channels in the current player."
            )
    async def rotation(self,
                       inter: disnake.ApplicationCommandInteraction,
                       frequency: float = commands.Param(default=2.0),
                       ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        filter = lavalink.filters.Rotation(frequency)
        await player.set_filter(filter)

        message = f"Applying a rotation filter with a frequency of {frequency}..."
        await inter.send(message, delete_after=8)

    @filter.sub_command(
            description="Clear all filters."
            )
    async def clear(self,
                    inter: disnake.ApplicationCommandInteraction
                    ) -> None:
        player = await create_player(inter, False)

        await inter.response.defer()

        await player.clear_filters()

        await inter.send("Clearing all filters...", delete_after=6)


def setup(bot: Stan) -> None:
    bot.add_cog(Bard(bot))

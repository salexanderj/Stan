import disnake
from disnake.ext import commands
import lavalink

from voice.voice_client import StanVoiceClient


async def create_player(inter: disnake.ApplicationCommandInteraction,
                        should_connect: bool = False) -> lavalink.DefaultPlayer:
    player = inter.bot.lavalink.player_manager.create(inter.guild.id)

    voice_client = inter.guild.voice_client

    if not inter.author.voice or not inter.author.voice.channel:
        if voice_client is not None:
            raise commands.CommandInvokeError('Join my channel.')
        raise commands.CommandInvokeError('Join a voicechannel, first.')

    voice_channel = inter.author.voice.channel

    if voice_client is None:
        if not should_connect:
            raise commands.CommandInvokeError('I\'m not playing music.')

        permissions = voice_channel.permissions_for(inter.me)

        if not permissions.connect or not permissions.speak:
            raise commands.CommandInvokeError('I need the \'CONNECT\' and \'SPEAK\' permissons.')

        if voice_channel.user_limit > 0:
            if len(voice_channel.members) >= voice_channel.user_limit and not inter.me.guild_permissions.move_members:
                raise commands.CommandInvokeError('Your voice channel is full.')

        player.store('channel', inter.channel.id)
        await inter.author.voice.channel.connect(cls=StanVoiceClient)
    elif voice_client.channel.id != voice_channel.id:
        raise commands.CommandInvokeError('You need to be in my voice channel.')

    return player

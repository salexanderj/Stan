import disnake
from disnake.ext import commands
from typing import Optional

from voice.voice_client import StanVoiceClient


def is_connected_to_voice(member: disnake.Member) -> bool:
    return member.voice is not None and member.voice.channel is not None


def try_get_voice_channel(member: disnake.Member) -> Optional[disnake.VoiceChannel]:
    if not is_connected_to_voice(member):
        return None

    return member.voice.channel


def try_get_voice_client(bot: commands.Bot, channel: disnake.VoiceChannel) -> Optional[StanVoiceClient]:
    vc: StanVoiceClient | disnake.VoiceProtocol = disnake.utils.get(bot.voice_clients, channel=channel)

    return vc


async def ensure_in_channel(bot: commands.Bot, channel: disnake.VoiceChannel) -> StanVoiceClient:
    vc = try_get_voice_client(bot, channel)
    if vc is None:
        vc = await channel.connect(reconnect=False, cls=StanVoiceClient)
    elif vc.channel is not channel:
        await vc.move_to(channel)

    return vc

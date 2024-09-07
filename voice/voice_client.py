import disnake
import asyncio
import lavalink
from lavalink.errors import ClientError

from config import LAVALINK_PASSWORD

class StanVoiceClient(disnake.VoiceProtocol):

    def __init__(self, client: disnake.Client, channel: disnake.abc.Connectable):
        self.client = client
        self.channel = channel
        self.guild_id = channel.guild.id
        self._destroyed = False

        if not hasattr(self.client, 'lavalink'):
            self.client.lavalink = lavalink.Client(client.user.id, player=StanPlayer)
            self.client.lavalink.add_node(host = 'localhost',
                                          port = 2333,
                                          password = LAVALINK_PASSWORD,
                                          region = 'us',
                                          name = 'default-node')


    async def on_voice_state_update(self, data) -> None:
        lavalink = self.client.lavalink

        channel_id = data['channel_id']
        if not channel_id:
            await self._destroy()
            return

        self.channel = self.client.get_channel(int(channel_id))

        lavalink_data = {
                't': 'VOICE_STATE_UPDATE',
                'd': data
                }
        await lavalink.voice_update_handler(lavalink_data)

    async def on_voice_server_update(self, data) -> None:
        lavalink = self.client.lavalink
        lavalink_data = {
                't': 'VOICE_SERVER_UPDATE',
                'd': data
                }
        await lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        lavalink = self.client.lavalink
        
        lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_deaf=self_deaf, self_mute=self_mute)

    async def disconnect(self, *, force: bool = False) -> None:
        player = self.client.lavalink.player_manager.get(self.channel.guild.id)
        
        if not force and not player.is_connected:
            return

        await self.channel.guild.change_voice_state(channel=None)

        player.channel_id = None
        await self._destroy()

    async def _destroy(self):
        self.cleanup()

        if self._destroyed:
            return
        self._destroyed = True

        try:
            await self.client.lavalink.player_manager.destroy(self.guild_id)
        except ClientError:
            pass

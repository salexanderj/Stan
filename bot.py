import os.path

import config
from disnake.ext import commands


class Stan(commands.Bot):

    def __init__(
            self,
            command_prefix=config.PREFIX,
            intents=config.INTENTS,
            sync_commands_debug=True,
            ):

        super().__init__(command_prefix=command_prefix,
                         intents=intents,
                         sync_commands_debug=sync_commands_debug)

        self._initialized = False

    async def on_ready(self) -> None:

        if not self._initialized:
            self._initialized = True

        await self.set_default_avatar()
        print("Stan initialized successfully.")

    async def set_default_avatar(self):
        user = self.user
        avatar_path = "avatar.png"
        if user is not None and os.path.exists(avatar_path):
            with open(avatar_path, 'rb') as avatar_file:
                avatar_data = avatar_file.read()
                await user.edit(username="Stan",
                                avatar=avatar_data)

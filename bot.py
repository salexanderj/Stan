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

            user = self.user
            avatar_path = "avatar.png"
            if user is not None and os.path.exists(avatar_path):
                with open(avatar_path, 'rb') as avatar_file:
                    avatar_data = avatar_file.read()
                    await user.edit(username="Stan",
                                    avatar=avatar_data)

                print("Stan initialized successfully.")

stan = Stan()
stan.load_extension('ext.radio')
stan.load_extension('ext.ripper')

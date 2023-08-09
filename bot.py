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


stan = Stan()
stan.load_extension("ext.radio")

import disnake
from os import environ

PREFIX = "%"
INTENTS = disnake.Intents.all()
TOKEN = environ['DISCORD_BOT_TOKEN']
LAVALINK_PASSWORD = environ['LAVALINK_SERVER_PASSWORD']

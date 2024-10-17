Notes:
* Requires ffmpeg in path or in the repository's root directory.
* Requires a current version of Lavalink.jar from https://github.com/lavalink-devs/Lavalink. The application.yml file in the lavalink directory must be in the same directory as the Lavalink.jar before you run it.
* The bot itself does not automate or manage the Lavalink/java process; you must start/manage it yourself seperately.
* Python's pip may fail to install lavalink.py due to a bug with its dependancy aiohttp's version requirement. I have placed the specific version of aiohttp that works within requirements.txt, but you may have to install manually lavalink.py with the --no-deps flag after ensuring the provided aiohttp version is installed.

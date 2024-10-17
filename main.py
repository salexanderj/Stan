import asyncio
from bot import Stan
from config import TOKEN


async def main() -> None:
    stan = Stan()
    await stan.login(TOKEN)
    stan.load_extensions('ext')
    await stan.connect()

if __name__ == "__main__":
    asyncio.run(main())

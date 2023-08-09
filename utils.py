import random


def random_chance(percent: float) -> bool:

    n = random.random() * 100.0
    print(n)

    if n <= percent:
        return True
    return False


def trim(string: str, length: int, ellipses: bool = True):

    return (string[:length] + "..." if ellipses else "") if len(string) > length else string
import asyncio

from MiPC import Misskey

async def note(text):
    mi = Misskey("server", "token")
    mi.send(text)

text = input(">")
asyncio.run(note(text))
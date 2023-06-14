import webbrowser
import time
import asyncio

from MiPC import MiAuth, MisskeyMiAuthFailedException, Misskey

server = input("server address>")
mia = MiAuth(server, "app name")
url = mia.generate_url() #permissions defult: ["read:account", "write:account", "read:blocks", "write:blocks", "read:drive", "write:drive", "read:favorites", "write:favorites", "read:following", "write:following", "read:messaging", "write:messaging", "read:mutes", "write:mutes", "write:notes", "read:notifications", "write:notifications", "write:reactions", "write:votes", "read:pages", "write:pages", "write:page-likes", "read:page-likes", "write:gallery-likes", "read:gallery-likes"]
webbrowser.open(url)

while True:
    try:
        auth_token = mia.get_token()
        break
    except MisskeyMiAuthFailedException:
        time.sleep(0.5)
        pass
    
async def note(text, token):
    mi = Misskey(server, token)
    mi.send(text)

text = input(">")
asyncio.run(note(text=text, token=auth_token))
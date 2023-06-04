# MiPC
MiPC (Misskey Python Client) is a Python client for using MisskeyAPI.

# Examples

##  MiAuth

```python

from MiPC.MiAuth import MiAuth

mia = MiAuth(server="misskey.io", name="TestApp")

url = mia.generate_url()

while True:

   try:

     auth_token = mia.get_token()

     break

   except MisskeyMiAuthFailedException:

     await asyncio.sleep(0.5)

     pass

```


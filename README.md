# This project has been discontinued.

**When installing, keep in mind that support is not provided by this library.**
# MiPC

![img](assets/icon.png)

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

# question
## Q. Why is the pypi registered under a different name(misskey-python) than MiPC?
A. Because the registration was denied due to the name being similar to an existing pypi project.

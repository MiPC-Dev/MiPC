import asyncio
import os
import uuid
from typing import (
    Optional,
    Union,
    List,
    Tuple,
    Set,
    Any,
    IO as IOTypes,
)
import zlib
import warnings

import mimetypes
import httpx
import websockets
import aiofiles
from colorama import Fore, Back, Style
from websockets import connect, exceptions
import orjson

from MiPC.MiAuth import MiAuth
from MiPC.exceptions import MisskeyMiAuthFailedException, MisskeyAPIException

class Misskey:
    
    def __init__(self, server, token, events={"on_note": "on_note"}):
        self.__server = server
        self.__token = token
        self.on_event = {}

    def __request_api(
        self,
        endpoint_name: str,
        **payload
    ) -> Union[dict, bool, List[dict]]:
        if self.__token is not None:
            payload['i'] = self.__token

        response = httpx.post(
            f'https://{self.__server}/api/{endpoint_name}',
            json=payload,
        )
        if response.status_code >= 400:
            raise MisskeyAPIException(response.json())

        if response.status_code == 204:
            return True
        else:
            return response.json()

    async def upload(
        self,
        file
    ):
        params = {
            'i' : self.__token,
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(
                url=f'https://{self.__server}/api/drive/files/create', 
                data=params,
                files={'file' : file}
            )
            return r

    async def delete(
        self,
        file_id: str
    ):
        return self.__request_api('drive/files/delete', fileId=file_id)

    def dispatch(self, name: str, *args):
        if name in self.on_event:
            for coro in self.on_event[name]:
                asyncio.create_task(coro(*args))

    async def start(self, channel=["main", "homeTimeline", "localTimeline", "hybridTimeline", "globalTimeline"], reconnect=True):
        while True:
            try:
                async for self.ws in websockets.connect(f'wss://{self.__server}/streaming?i={self.__token}'):
                    self.open = True
                    for i in range(len(channel)):
                        print(f"connecting channel to: {channel[i]}")
                        await self.ws.send(orjson.dumps({
                            "type": "connect",
                            "body": {
                                "channel": channel[i],
                                "id": channel[i]
                            }
                        }))
                        print(f"connected channel: {channel[i]}")
                    while True:
                        data = orjson.loads(zlib.decompress(await self.ws.recv()))
                        print("---------------------------")
                        print(data)
                        print("---------------------------")
            except:
                warnings.warn('Connection Error. Reconnecting...')
                continue

    async def close(self):
        self.open=False
        await self.ws.close()

    async def recv(self):
        try:
            data = orjson.loads(zlib.decompress(await self.ws.recv()))
            if data["type"] == "channel":
                print(data)
            else:
                print("---------------------------")
                print(data)
                print("---------------------------")
        except exceptions.ConnectionClosed:
            await self.on_close()
        else:
            if data["type"] == "channel":
                print(data)

        def on(self, name: str):
            def deco(coro):
                if name in self.on_event:
                    self.on_event[name].append(coro)
                else:
                    self.on_event[name] = [coro]
                return coro
            return deco

async def test():
    mia = MiAuth(server="misskey.io", name="TestApp")
    print(mia.generate_url())
    while True:
        try:
            auth_token = mia.get_token()
            break
        except MisskeyMiAuthFailedException:
            await asyncio.sleep(0.5)
            pass
    api = Misskey(server="misskey.io", token=auth_token)
    await api.start()

asyncio.run(test())
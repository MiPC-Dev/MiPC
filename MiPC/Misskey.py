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
import json
import sys

import mimetypes
import httpx
import websockets
import aiofiles
from colorama import Fore, Back, Style
from websockets import connect, exceptions
import orjson

from MiPC.MiAuth import MiAuth
from MiPC.exceptions import MisskeyMiAuthFailedException, MisskeyAPIException

class user:
    pass

class Misskey:
    
    def __init__(
        self, server, token=None):
        self.__server = server
        self.__token = token

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

    async def meta(
        self):
        class metadata:
            pass
        print(self.__token)
        params = {
            "i" : self.__token,
        }
        headers = {
            "Content-Type": "application/json",
            "i" : self.__token
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(
                url=f'https://{self.__server}/api/meta', 
                json=params,
                headers=headers
            )
            rj = r.json()
            meta = metadata
            try:
                meta.maintainer = [rj["maintainerName"], rj["maintainerEmail"]]
                meta.version = rj["version"]
                meta.name = rj["name"]
                meta.url = rj["uri"]
                meta.description = rj["description"]
                meta.lang = rj["langs"]
                meta.tos = rj["tosUrl"]
                meta.full = json.dumps(rj, ensure_ascii=False, indent=4)
                return meta
            except KeyError:
                print(r.text)
                print("-----------------")
                print(r.json)

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
                files={"file" : file}
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

    async def send(self, text, visibility="public", visibleUserIds: list=None, replyid=None, fileid=None, channelId=None, localOnly=False):
        url = f"https://{self.__server}/api/notes/create"
        if replyid is not None:
            if fileid is not None:
                params = {
                    "i" : self.__token,
                    "replyId": replyid,
                    "fileIds": fileid,
                    "visibility": visibility,
                    "visibleUserIds": visibleUserIds,
                    "channelId": channelId,
                    "localOnly": localOnly,
                    "text": text
                }
                head = {
                    "Content-Type": "application/json"
                }
                async with httpx.AsyncClient() as client:
                    r = await client.post(
                        url=url, 
                        json=params,
                        headers=head
                    )
                    return r.json()
            else:
                params = {
                    "i" : self.__token,
                    "replyId": replyid,
                    "visibility": visibility,
                    "visibleUserIds": visibleUserIds,
                    "channelId": channelId,
                    "localOnly": localOnly,
                    "text": text
                }
                head = {
                    "Content-Type": "application/json"
                }
                async with httpx.AsyncClient() as client:
                    r = await client.post(
                        url=url, 
                        json=params,
                        headers=head
                    )
                    return r.json()
        else:
            params = {
                "i" : self.__token,
                "text": text
            }
            head = {
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url=url, 
                    json=params,
                    headers=head
                )
                return r.json()

    async def renote(self, rid: str, quote: str=None, visibility="public", visibleUserIds: list=None, channelId=None, localOnly=False):
        url = f"https://{self.__server}/api/notes/create"
        if quote is None:
            params = {
                "i" : self.__token,
                "renoteId": rid,
                "localOnly": localOnly,
                "channelId": channelId,
            }
            head = {
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url=url, 
                    json=params,
                    headers=head
                )
                return r.json()
        else:
            params = {
                "i" : self.__token,
                "renoteId": rid,
                "visibility": visibility,
                "visibleUserIds": visibleUserIds,
                "localOnly": localOnly,
                "channelId": channelId,
                "text": quote
            }
            head = {
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url=url, 
                    json=params,
                    headers=head
                )
                return r.json()

async def test():
    mia = MiAuth(server="misskey.io", name="MiPC-Dev0.1")
    print(mia.generate_url())
    while True:
        try:
            auth_token = mia.get_token()
            break
        except MisskeyMiAuthFailedException:
            await asyncio.sleep(0.5)
            pass
    api = Misskey(server="misskey.io", token=auth_token)
    await asyncio.sleep(2)
    r = await api.meta()
    try:
        print("----------------------------")
        print(r.name)
        print(r.description)
        print(r.url)
        print("----------------------------")
    except AttributeError:
        r = await api.meta()
        print("----------------------------")
        print(r.name)
        print(r.description)
        print(r.url)
        print("----------------------------")
    a = await api.send("test")
    print(a)
    await asyncio.sleep(1.5)
    b = await api.renote("9fmea4z1dn")
    print(b)
    await asyncio.sleep(1.5)
    c = await api.renote("9fmea4z1dn", "Quote Test")
    print(c)
    await asyncio.sleep(1.5)
    d = await api.send("Reply Test", "9fmea4z1dn")
    print(d)
    sys.exit()

asyncio.run(test())
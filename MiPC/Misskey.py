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
import traceback
import re

import mimetypes
import httpx
import websockets
import aiofiles
from colorama import Fore, Back, Style
from websockets import connect, exceptions
import orjson

from MiPC.exceptions import MisskeyMiAuthFailedException, MisskeyAPIException
from MiPC import mihttp

class user:
    pass

class Misskey:
    
    def __init__(
        self, server, token=None):
        self.__pattern = "http?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        self.__pattern_ws = "^ws:\/\/.*"
        if re.match(self.__pattern_ws, server):
            raise TypeError("Websocket procotr is not available within the Misskey class.")
        if re.match(self.__pattern, server):
            self.__server = server
        else:
            self.__server = "https://" + server
        self.__token = token
        self.http = mihttp(server)

    async def meta(
        self):
        class metadata:
            pass
        params = {
            "i" : self.__token,
        }
        headers = {
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(
                url=f'{self.__server}/api/meta', 
                json=params,
                headers=headers
            )
            rj = json.loads(r.text)
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
            except Exception as e:
                raise MisskeyAPIException(f"Failed to retrieve metadata. status code: {r.status_code}\n\n{traceback.format_exc()}")

    async def upload(
        self,
        file
    ):
        params = {
            'i' : self.__token,
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(
                url=f'{self.__server}/api/drive/files/create', 
                data=params,
                files={"file" : file}
            )
            return r

    async def delete(
        self,
        file_id: str
    ):
        return self.http.request('drive/files/delete', data={
            "fileId": file_id
        })

    async def send(self, text, visibility="public", visibleUserIds: list=None, replyid=None, fileid=None, channelId=None, localOnly=False):
        url = f"{self.__server}/api/notes/create"
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
                if visibleUserIds is None:
                    params = {
                        "i" : self.__token,
                        "replyId": replyid,
                        "visibility": visibility,
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
        url = f"{self.__server}/api/notes/create"
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
            if visibleUserIds is None:
                params = {
                    "i" : self.__token,
                    "renoteId": rid,
                    "visibility": visibility,
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
                
class StreamingClient():

    class context:
        pass

    def __init__(self, server, token):
        self.__token = token
        self.__pattern = "^ws:\/\/.*"
        if re.match(self.__pattern, server):
            self.__server = server
        else:
            self.__server = "wss://" + server

    def run(self):
        async def runner(self):
            self.__ws = await websockets.connect(f'wss://{self.__server}/streaming?i={self.__token}')
            try:
                await self.on_ready()
            except AttributeError:
                pass
            while True:
                response = await self.recv()
                response = json.loads(response)
                if response["body"]["type"] == "note":
                    try:
                        ctx = self.context()
                        ctx.note.id = response["body"]["body"]["id"]
                        ctx.author.id = response["body"]["body"]["userId"]
                        ctx.author.name = response["body"]["body"]["user"]["name"]
                        ctx.author.username = response["body"]["body"]["user"]["username"]
                        ctx.text = response["body"]["body"]["text"]
                        ctx.reactions = response["body"]["body"]["reactions"]
                        ctx.files = response["body"]["body"]["files"]
                        ctx.fileId = response["body"]["body"]["fileIds"]
                        ctx.reply.id = response["body"]["body"]["replyId"]
                        ctx.renote.id = response["body"]["body"]["renoteId"]
                        ctx.uri = response["body"]["body"]["uri"]
                        ctx.url = response["body"]["body"]["url"]
                        if response["body"]["body"]["user"]["host"] is not None:
                            ctx.author.host = response["body"]["body"]["user"]["host"]
                            ctx.author.host.name = response["body"]["body"]["user"]["instance"]["name"]
                            ctx.author.host.software = response["body"]["body"]["user"]["instance"]["softwareName"]
                            ctx.author.host.softwareversion = response["body"]["body"]["user"]["instance"]["softwareVersion"]
                            ctx.author.host.icon = response["body"]["body"]["user"]["instance"]["iconUrl"]
                            ctx.author.host.favicon = response["body"]["body"]["user"]["instance"]["faviconUrl"]
                            ctx.author.host.color = response["body"]["body"]["user"]["instance"]["themeColor"]
                        else:
                            ctx.author.host = None
                        await self.on_note(ctx)
                    except AttributeError:
                        pass
        asyncio.run(runner(self))

    async def send(self, message):
        await self.__ws.send(json.dumps(message, indent=4, ensure_ascii=False))

    async def connect(self, channel):
        await self.__ws.send(json.dumps({"type": "connect", "body": {"channel": channel, "id": channel}}, indent=4, ensure_ascii=False))

    async def disconnect(self, channel):
        await self.__ws.send(json.dumps({"type": "disconnect", "body": {"id": channel}}, indent=4, ensure_ascii=False))


    async def recv(self):
        return await self.__ws.recv()
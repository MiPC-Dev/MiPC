import httpx

from MiPC.exceptions import MisskeyMiAuthFailedException, MisskeyAPIException

class mihttp:
    
    def __init__(self, base_url):
        self.__base = base_url
    
    async def request(
        self, endpoint, data, file=None
    ):
        head = {
            "Content-Type": "application/json"
        }
        if file is not None:
            async with httpx.AsyncClient(base_url=self.__base) as client:
                async with client.post(endpoint, json=data, headers=head, files=file) as response:
                    if response.status_code >= 400:
                        raise MisskeyAPIException(response.json())

                    if response.status_code == 204:
                        return True
                    else:
                        return response.json()
        else:
            async with httpx.AsyncClient(base_url=self.__base) as client:
                async with client.post(endpoint, json=data, headers=head) as response:
                    if response.status_code >= 400:
                        raise MisskeyAPIException(response.json())

                    if response.status_code == 204:
                        return True
                    else:
                        return response.json()

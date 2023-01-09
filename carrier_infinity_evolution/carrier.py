import argparse
import asyncio
import xml.etree.ElementTree as ETree
from contextlib import AsyncExitStack
from typing import Optional, Any

import aiohttp
from multidict import CIMultiDict
import yarl
from oauthlib.oauth1.rfc5849 import Client as OAuth1Client


class AIOOAuth1Client(aiohttp.ClientRequest):
    def update_auth(self, auth: Optional[OAuth1Client]) -> None:
        self.auth = auth

    def update_body_from_data(self, body: Any) -> None:
        super().update_body_from_data(body)

        self.auth: OAuth1Client
        self.auth.realm = self.url
        uri, headers, body = self.auth.sign(
            str(self.url), self.method, self.body._value if self.body else None, self.headers, str(self.url)
        )
        self.url = yarl.URL(uri)
        self.headers = CIMultiDict(headers)
        if body:
            self.body._value = body.encode('utf-8')


# https://openapi.ing.carrier.com/docs
class CarrierInfinity:
    def __init__(self, base_url: yarl.URL, client_key: str, client_secret: str, user_name: str, password: str):
        self._base_url = base_url
        self._client_key = client_key
        self._client_secret = client_secret
        self._user_name = user_name
        self._password = password

        self._access_token = None
        self._exit_stack = AsyncExitStack()
        self._session: Optional[aiohttp.ClientSession] = None
        self._oauth1 = OAuth1Client(client_key, client_secret)

    async def __aenter__(self):
        self._session = await self._exit_stack.enter_async_context(aiohttp.ClientSession(request_class=AIOOAuth1Client, auth=self._oauth1))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)

    async def _ensure_auth(self):
        if self._access_token:
            return

        # TODO: do they support json payload instead?
        root = ETree.Element("credentials")
        for k, v in {'username': self._user_name, 'password': self._password}.items():
            e = ETree.Element(k)
            e.text = v
            root.append(e)

        data = {'data': ETree.tostring(root).decode('utf-8')}
        form_data = aiohttp.FormData(data)

        url = self._base_url / 'users/authenticated'

        headers = {
            "featureset": "CONSUMER_PORTAL",
            'Accept': 'application/json'
        }
        async with self._session.post(url, data=form_data, headers=headers) as r:
            assert r.status == 200, (r.status, r.reason, await r.text())
            data = await r.json()

        self._access_token = data['result']['accessToken']

    async def _request(self, method: str = 'get', *, url: str):
        await self._ensure_auth()

        url = self._base_url / url
        self._oauth1.resource_owner_key = self._user_name
        self._oauth1.resource_owner_secret = self._access_token
        headers = {
            "featureset": "CONSUMER_PORTAL",
            'Accept': 'application/json'
        }
        async with self._session.request(method, url, headers=headers) as r:
            assert r.status == 200, (r.status, r.reason, await r.text())
            return await r.json()

    async def get_user_info(self):
        data = await self._request(url=f'users/{self._user_name}')
        return data


async def main():
    parser = argparse.ArgumentParser(description='Carrier Infinity/Evolution API Client')

    # these can be obtained from source of https://www.myinfinitytouch.carrier.com/login
    parser.add_argument('-client_key', type=str, required=True, help='Carrier API Client Key')
    parser.add_argument('-client_secret', type=str, required=True, help='Carrier API Client Secret')

    parser.add_argument('-base_url', type=yarl.URL, default=yarl.URL('https://www.app-api.ing.carrier.com'), help='Carrier API Base URL')
    parser.add_argument('-user_email', type=str, required=True, help='Carrier API User/Email')
    parser.add_argument('-user_email_password', type=str, required=True, help='Carrier API User/Email Password')

    app_args = parser.parse_args()

    async with CarrierInfinity(
        app_args.base_url, app_args.client_key, app_args.client_secret,
        app_args.user_email, app_args.user_email_password
    ) as carrier:
        data = await carrier.get_user_info()
        print(data)


if __name__ == '__main__':
    asyncio.run(main())

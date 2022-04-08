import aiohttp
from typing import Union
import logging
import html
import json


async def aiohttp_get(
    url: str, _type: Union[str, None] = "json", headers=None
) -> Union[str, bytes, dict]:
    async with aiohttp.ClientSession() as session:

        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logging.info(f"aiohttp_get: {url} returned {response.status}")
                return None
            if _type == "json":
                json = await response.json()
                return json
            elif _type == "text":
                text = await response.text()
                return html.unescape(text)

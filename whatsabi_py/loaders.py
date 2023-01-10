from typing import List
import aiohttp
import asyncio
from web3 import Web3
from abc import ABC, abstractclassmethod


class ABILoader(ABC):
    @abstractclassmethod
    def load_abi(self, address):
        pass


class EtherscanLoader(ABILoader):
    api_key: str
    base_url: str

    def __init__(self, config={}):
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "https://api.etherscan.io/api")

    async def load_abi(self, address):
        url = (
            self.base_url
            + "?module=contract&action=getabi&address="
            + address
            + "&apikey="
            + self.api_key
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return data["result"]


class SourcifyABILoader(ABILoader):
    base_url: str = "https://repo.sourcify.dev/contracts/partial_match/1/"

    async def load_abi(self, address):
        address = Web3.toChecksumAddress(address)
        url = self.base_url + address + "/metadata.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return data["output"]["abi"]


class SignatureLookup(ABC):
    @abstractclassmethod
    def load_functions(self, selector) -> List[str]:
        pass

    @abstractclassmethod
    def load_events(self, hash) -> List[str]:
        pass


class SamczsunSignatureLookup(SignatureLookup):
    function_base_url: str = "https://sig.eth.samczsun.com/api/v1/signatures?function="
    event_base_url: str = "https://sig.eth.samczsun.com/api/v1/signatures?event="

    async def load(self, url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data["result"]
        except Exception as error:
            raise error

    async def load_functions(self, selector):
        result = await self.load(self.function_base_url + selector)
        return [signature["name"] for signature in result["function"][selector]]

    async def load_events(self, hash):
        result = await self.load(self.event_base_url + hash)
        return [signature["name"] for signature in result["event"][hash]]


class FourByteSignatureLookup(SignatureLookup):
    function_base_url: str = (
        "https://www.4byte.directory/api/v1/signatures/?hex_signature="
    )
    event_base_url: str = (
        "https://www.4byte.directory/api/v1/event-signatures/?hex_signature="
    )

    async def load(self, url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data["results"]
        except Exception as error:
            raise error

    async def load_functions(self, selector):
        result = await self.load(self.function_base_url + selector)
        return [signature["text_signature"] for signature in result]

    async def load_events(self, hash):
        result = await self.load(self.event_base_url + hash)
        return [signature["text_signature"] for signature in result]


class MultiSignatureLookup(SignatureLookup):
    lookups: List[SignatureLookup]

    def __init__(self, lookups) -> None:
        self.lookups = lookups

    async def load_functions(self, selector):
        tasks = [lookup.load_functions(selector) for lookup in self.lookups]
        signatures = await asyncio.gather(*tasks)
        return list(
            set([sig for sub_signatures in signatures for sig in sub_signatures])
        )

    async def load_events(self, hash):
        tasks = [lookup.load_events(hash) for lookup in self.lookups]
        signatures = await asyncio.gather(*tasks)
        return list(
            set([sig for sub_signatures in signatures for sig in sub_signatures])
        )

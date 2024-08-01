import aiohttp
import asyncio
from itertools import cycle

class AsyncAPIManager:
    def __init__(self, api_keys):
        self.api_keys = cycle(api_keys)
        self.current_api_key = next(self.api_keys)

    async def get(self, url, params=None):
        if params is None:
            params = {}
        while True:
            params["api_key"] = self.current_api_key
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, timeout=10) as response:
                        if response.status == 429:
                            print("Rate limit exceeded. Switching API key...")
                            self.current_api_key = next(self.api_keys)
                            print(f"New API key: {self.current_api_key}")
                            await asyncio.sleep(5)  # Sleep for a second before retrying
                            continue
                        elif response.status == 200:
                            try:
                                return await response.json(), response.status
                            except aiohttp.ClientPayloadError as e:
                                print(f"Failed to parse JSON response: {e}")
                                return {"data": []}, response.status
                            except aiohttp.ClientConnectionError as e:
                                print(f"Connection closed unexpectedly: {e}")
                                self.current_api_key = next(self.api_keys)
                                await asyncio.sleep(5)
                                continue
                        else:
                            print(f"Error: {response.status}")
                            return {"data": []}, response.status
            except asyncio.TimeoutError:
                print('Request timed out')
                return {"data": []}, response.status
            except aiohttp.ClientError as e:
                print(f"Request failed: {e}")
                self.current_api_key = next(self.api_keys)
                await asyncio.sleep(1)

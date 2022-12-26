from __future__ import annotations

__all__ = ['CountryFlags']

import aiofiles

from aiohttp import ClientSession
from os import getcwd

BASE_URL = "https://countryflagsapi.com"

class CountryFlags:
	def __init__(self) -> None:
		self.session: ClientSession | None = None

	async def __aenter__(self) -> "CountryFlags":
		self.session = ClientSession()
		return self

	async def close_session(self) -> None:
		if self.session is not None:
			await self.session.close()

	async def __aexit__(self, *_args) -> None:
		await self.close_session()


	async def get(self, code: str, file_name: str | None = None, file_type: str = "png", save_location: str | None = None) -> int:
		if self.session is None:
			self.session = ClientSession()

		async with self.session.get(BASE_URL + f"/{file_type}" + f"/{code}") as response:
			if response.status == 200:
				async with aiofiles.open(f"{save_location or getcwd()}/{file_name or code}.{file_type}", mode='wb+') as f:
					await f.write(await response.read())

			return response.status
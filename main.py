from os import environ
from traceback import print_tb

from discord import Status, Game, Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv('.env')

from utils import Default, log


class GuessTheFlagCountry(Bot):
	def __init__(self) -> None:
		super().__init__(
			command_prefix=".",
			case_sensitive=False,
			status=Status.online,
			intents=Intents.default(),
			activity=Game("/play"),
			application_id=environ.get("APP_ID"),
			description="guess flag country boss"
		)


	async def on_ready(self) -> None:
		log("status", "running")


	async def setup_hook(self) -> None:
		try:
			await self.tree.sync()
			await self.tree.sync(guild=Default.test_server)
		except Exception as e:
			log("error", "failed to sync commands")
			print_tb(e)
		else:
			log("status", "synced commands")

bot = GuessTheFlagCountry()


from discord.app_commands import guilds
from discord import Interaction as Inter, File, Embed, User, Member, ButtonStyle, TextStyle

from countryflags import CountryFlags

from os import getcwd, listdir
from json import loads

# Data from https://gist.github.com/keeguon/2310008
COUNTRY_CODES: list[dict['name': str, 'code': str]] = {}

with open(f"{getcwd()}/codes.json", 'r') as f:
	COUNTRY_CODES = loads(f.read())


from discord.ui import View, Button, Modal, TextInput

TIMEOUT: float = 300.0


class BaseView(View):
	def __init__(self, author: User | Member) -> None:
		self.author: User | Member = author

		super().__init__(timeout=TIMEOUT)

	async def interaction_check(self, inter: Inter) -> bool:
		return inter.user.id == self.author.id


class PlayGuessModal(Modal):
	answer: TextInput = TextInput(label="Answer", style=TextStyle.short, placeholder="country name")

	def __init__(self, view: BaseView, correct_answer: str) -> None:
		self.view: BaseView = view
		self.correct_answer: str = correct_answer

		super().__init__(title="Guess the flag country!", timeout=TIMEOUT)

	async def on_submit(self, inter: Inter) -> None:
		answer: str = self.answer.value

		result: bool = self.correct_answer.replace("'", '').lower() == answer.replace("'", '').strip().lower()
		
		await inter.response.send_message(f"{':white_check_mark:' if result else ':x:'} `{answer}` is **{'' if result else 'in'}correct**", ephemeral=not result)

		if result:
			self.view.stop()


class PlayGuessButton(Button):
	def __init__(self, correct_answer: str) -> None:
		self.correct_answer: str = correct_answer

		super().__init__(style=ButtonStyle.green, label="Guess")

	async def callback(self, inter: Inter) -> None:
		await inter.response.send_modal(PlayGuessModal(self.view, self.correct_answer))


import random
from time import time
from datetime import timedelta
from humanize import precisedelta

FLAGS_PATH: str = f"{getcwd()}/flags/"

from discord.ext.tasks import loop


@loop(seconds=30.0, count=5)
async def timer(start_time: float, inter: Inter, embed: Embed) -> None:
	remaining_time: float = TIMEOUT - (time() - start_time)

	log("debug", f"remaining_time: {remaining_time}")

	embed.set_footer(icon_url=inter.user.avatar.url, text=f"{inter.user} | {'⚠️' if remaining_time <= 30.0 else ''} {precisedelta(timedelta(seconds=round(remaining_time)), format='%0.0f')} left")

	await inter.edit_original_response(embed=embed)


@bot.tree.command(description="Play guess the flag")
@guilds(Default.test_server)
async def play(inter: Inter) -> None:
	country: str = random.choice(COUNTRY_CODES)

	if f"{country['code']}.png" not in listdir(FLAGS_PATH):
		async with CountryFlags() as session:
			status: int = await session.get(country['code'], save_location=FLAGS_PATH)

			if status != 200:
				await inter.response.send_message("Something went wrong :sob:", ephemeral=True)

				log("error", f"command play raised status code {status} when trying to get a flag", True)

	embed: Embed = Embed(title="Guess the flag country!", color=Default.color, description=f"Cheat: ||{country['name']}||")

	file_name: str = f"{country['code']}.png"

	embed.set_image(url=f"attachment://{file_name}")

	view: BaseView = BaseView(inter.user)
	view.add_item(PlayGuessButton(country['name']))

	await inter.response.send_message(file=File(f"{FLAGS_PATH}/{file_name}", filename=file_name), embed=embed, view=view)

	timer.start(time(), inter, embed)

	await view.wait()

	timer.cancel()

	embed.description = f"Answer: ||{country['name']}||"
	embed.set_footer(icon_url=inter.user.avatar.url, text=inter.user)

	await inter.edit_original_response(embed=embed, view=None)


if __name__ == '__main__':
	bot.run(environ.get("TOKEN"))
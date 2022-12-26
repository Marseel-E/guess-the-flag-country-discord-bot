__all__ = ['log', 'Color', 'Default']


from datetime import datetime

def log(title: str, message: str, error: bool = False):
	if error:
		raise Exception(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] [{title.upper()}]: {message}")

	margin = ""
	if len(title) < 8:
		margin = int(8 - len(title)) * " "

	print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] [{title.upper()}{margin}]: {message}")


from discord import Object as D_Object

from dataclasses import dataclass


@dataclass
class Color:
	blurple: int = int("5261f8", 16)
	green: int = int("77DD77", 16)

@dataclass
class Default:
	test_server: D_Object = D_Object(id=843994109366501376)
	color: int = Color.blurple
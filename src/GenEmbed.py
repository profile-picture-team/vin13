import enum
import discord

class EmbedTypes(enum.Enum):
	info    = (0x007D80, "{text}")
	ok      = (0x006b12, ":white_check_mark: {text}")
	warning = (0xadad00, ":warning: {text}")
	error   = (0xa30000, ":anger: {text}")

def get_embed(text, type = EmbedTypes.info):
	""" Генерирует discord.Embed  """
	color, msg = type
	return discord.Embed(description=msg.format(text=text), colour=color)


def get_info_embed(text):
	""" Генерирует discord.Embed используя EmbedTypes.info """
	color, msg = EmbedTypes.info
	return discord.Embed(description=msg.format(text=text), colour=color)


def get_ok_embed(text):
	""" Генерирует discord.Embed используя EmbedTypes.ok """
	color, msg = EmbedTypes.ok
	return discord.Embed(description=msg.format(text=text), colour=color)


def get_warning_embed(text):
	""" Генерирует discord.Embed используя EmbedTypes.warning """
	color, msg = EmbedTypes.warning
	return discord.Embed(description=msg.format(text=text), colour=color)


def get_error_embed(text):
	""" Генерирует discord.Embed используя EmbedTypes.error """
	color, msg = EmbedTypes.error
	return discord.Embed(description=msg.format(text=text), colour=color)

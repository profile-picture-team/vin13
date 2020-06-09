import enum
import discord

class EmbedTypes(enum.Enum):
	info    = (0x007D80, "{text}")
	ok      = (0x006b12, ":white_check_mark: {text}")
	warning = (0xadad00, ":warning: {text}")
	error   = (0xa30000, ":anger: {text}")

def get_embed(text, type = EmbedTypes.info):
	""" Генерирует discord.Embed  """
	return discord.Embed(description=type[1].format(text=text), colour=type[0])

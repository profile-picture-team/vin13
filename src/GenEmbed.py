import discord


class MsgEmbed:
	""" Генератор сообщений в Embed'ах """

	class Types:
		""" Типы Embed'ов """
		info    = (0x007D80, "{msg}")
		ok      = (0x006b12, ":white_check_mark: {msg}")
		warning = (0xadad00, ":warning: {msg}")
		error   = (0xa30000, ":anger: {msg}")


	def get(type: Types, msg: str) -> discord.Embed:
		""" Возвращает Embed типа type с сообщением msg """
		color, msg_template = type
		return discord.Embed(description=msg_template.format(msg=msg), colour=color)

	
	def info(msg: str) -> discord.Embed:
		""" Возвращает Embed типа info с сообщением msg """
		color, msg_template = MsgEmbed.Types.info
		return discord.Embed(description=msg_template.format(msg=msg), colour=color)

	
	def ok(msg: str) -> discord.Embed:
		""" Возвращает Embed типа ok с сообщением msg """
		color, msg_template = MsgEmbed.Types.ok
		return discord.Embed(description=msg_template.format(msg=msg), colour=color)

	
	def warning(msg: str) -> discord.Embed:
		""" Возвращает Embed типа warning с сообщением msg """
		color, msg_template = MsgEmbed.Types.warning
		return discord.Embed(description=msg_template.format(msg=msg), colour=color)

	
	def error(msg: str) -> discord.Embed:
		""" Возвращает Embed типа error с сообщением msg """
		color, msg_template = MsgEmbed.Types.error
		return discord.Embed(description=msg_template.format(msg=msg), colour=color)

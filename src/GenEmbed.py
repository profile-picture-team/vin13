from discord import Embed
from typing import Callable

class _MsgEmbed:
	""" Генератор сообщений в discord.Embed'ах """

	class Types:
		""" Типы discord.Embed'ов """
		info    = (0x007D80, "{msg}")
		ok      = (0x006b12, ":white_check_mark: {msg}")
		warning = (0xadad00, ":warning: {msg}")
		error   = (0xa30000, ":anger: {msg}")
		hearts  = (0xd72d42, "{msg} :two_hearts:")


	def __getattr__(self, name) -> Callable[[str], Embed]:
		def wrapper(msg: str) -> Embed:
			return self.get(getattr(self.Types, name), msg)
		return wrapper


	def get(self, type: Types, msg: str) -> Embed:
		""" Возвращает discord.Embed типа type с сообщением msg """
		color, msg_template = type
		return Embed(description=msg_template.format(msg=msg), colour=color)


MsgEmbed = _MsgEmbed()

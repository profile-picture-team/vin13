import enum
import re
from typing import *
import requests

import logging
logger = logging.getLogger(__name__)

from MusicInfo import MusicInfo

class VkSearch:

	class Types(enum.Enum):
		byString      = 0
		byPlaylistId  = 1
		byPlaylistUrl = 2

	icons = {
		'default-music' : 'https://img.icons8.com/pastel-glyph/FFFFFF/music-record.png'
	}
	api_root = 'https://vk.music7s.cc'
	session = requests.Session()

	def __new__(cls, search_type: Types, *args, **kwargs) -> Optional[List[MusicInfo]]:
		func = {
			cls.Types.byString      : cls.byString,
			cls.Types.byPlaylistId  : cls.byPlaylistId,
			cls.Types.byPlaylistUrl : cls.byPlaylistUrl
		}.get(search_type, None)
		if callable(func): return func(*args, **kwargs)
		return None

	
	@classmethod
	def byString(cls, q: str, count: int = 0) -> Optional[List[MusicInfo]]:
		data = cls.ApiRequest('search.php', {'search' : q})
		if data is None: return None

		if data['error']:
			if 'items' not in data:
				logger.warning(f'Search request. Error message: {data["error_message"]}')
			return []

		items = data['items']
		if count > 0: items = items[:count]
		return cls.ApiItemsToMIList(items)


	@classmethod
	def byPlaylistId(cls, playlist_id: str) -> Optional[List[MusicInfo]]:
		data = cls.ApiRequest('get_playlist.php', {'id' : playlist_id})
		if data is None: return None

		if data['error']:
			if 'items' not in data:
				logger.warning(f'Get playlist by id request. Error message: {data["error_message"]}')
			return []

		items = data['items']
		return cls.ApiItemsToMIList(items)


	@classmethod
	def byPlaylistUrl(cls, playlist_url: str) -> Optional[List[MusicInfo]]:
		match = re.search(r'\d+_\d+$', playlist_url)
		if match is None: return None
		return cls.byPlaylistId(match.group(0))


	@classmethod
	def ApiRequest(cls, method: str, args: dict = dict()) -> Optional[dict]:
		"""
			Отправляет запрос на апи vk.music7c.cc
			Дата последней проверки апи: 27.05.2020
		"""
		try:
			logger.debug(f'Api request, method: {method}')
			url = cls.urlJoin(cls.api_root, 'api', method)
			response = cls.session.get(url, params=args, timeout=10)
			response.raise_for_status()
			return response.json()
		except requests.Timeout as err:
			logger.error(f'Get: {err.request.url} - Timed out.')
		except requests.HTTPError as err:
			logger.error(f'Get: {err.request.url} - Bad answer: {err.request.status_code}.')
		except requests.ConnectionError as err:
			logger.error(f'Get: {err.request.url} - Connection error')
		except requests.RequestException as err:
			logger.exception(f'Get: {err.request.url} - Unforeseen exception')


	@classmethod
	def ApiItemsToMIList(cls, items) -> List[MusicInfo]:
		result = list()
		for item in items:
			new_mi = cls.ApiItemToMI(item)
			if new_mi is not None: result.append(new_mi)
		return result


	@classmethod
	def ApiItemToMI(cls, item: dict) -> Optional[MusicInfo]:
		mi = MusicInfo()
		mi.artist = item.get('artist')
		mi.title = item.get('title')
		mi.image_url = item.get('image')
		filepath = str(item.get('url'))
		if filepath is not None:
			mi.filepath =  cls.urlJoin(cls.api_root, filepath)
		time_str = str(item.get('duration'))
		if time_str is not None:
			mi.time = sum([
				a * b for a, b in zip(
					[3600, 60, 1],
					map(int, time_str.split(':'))
				)
			])
		else:
			# ПИ**ЕЦ НА**Й, ССЫЛКИ НЕТ!!!
			logger.critical(f'ППЦ ССЫЛКИ НЕТУ!!!')
			return None

		if mi.image_url is None: mi.image_url = cls.icons['default-music']
		if mi.artist is None: logger.warning(f'{mi.filepath} - artist is None'); mi.artist = 'Ауешник'
		if mi.title  is None: logger.warning(f'{mi.filepath} - title is None');  mi.title  = 'ошибся'
		if mi.time   is None: logger.warning(f'{mi.filepath} - time is None');   mi.time   = 0

		return mi


	def urlJoin(*args) -> str:
		return '/'.join(s.strip('/') for s in args)


	def isCorrectPlaylistUrl(url: str) -> bool:
		return \
			re.fullmatch(r'https?://vk.com/music/playlist/\d+_\d+', url) is not None

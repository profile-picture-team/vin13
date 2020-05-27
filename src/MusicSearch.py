import time
import os.path
import requests

from Playlist import Playlist

import logging
logger = logging.getLogger(__name__)

def musicSearch(service, q, count = 0):
	""" Вызывает функцию поиска для соответствующего сервиса """
	service = str(service)
	if service.lower() == 'vk': return Playlist.musicSearchVK(q, count)

def musicSearchVK(q, count = 0):
	"""
		Отправляет поисковый запрос на vk.music7c.cc
		Возвращает список объектов MusicInfo
		При ошибке возвращает None

		Дата последней проверки апи: 27.05.2020
	"""
	try:
		logger.info(f'Search request: {q}')
		url = 'https://vk.music7s.cc/api/search.php'
		params = {'search' : q, 'time' : time.time()}
		response = requests.get(url, params=params, timeout=10)
		response.raise_for_status()
		data = response.json()
	except requests.Timeout:
		logger.error(f'Get: {response.url} - Timed out.')
	except requests.HTTPError as err:
		logger.error(f'Get: {response.url} - Bad answer: {err.response.status_code}.')
	except requests.ConnectionError:
		logger.error(f'Get: {response.url} - Connection error')
	except requests.RequestException:
		logger.exception(f'Get: {response.url} - Unforeseen exception')
	else:
		if data['error']:
			if data['error_message'][:34] != 'Не удалось получить список музыки.':
				logger.warning(f'Get: {response.url} - Error message: {data["error_message"]}')
			return []

		# пакуем полученные данные в MusicInfo
		items = data['items'][:count] if count != 0 else data['items']
		result = list()
		for item in items:
			mi = Playlist.MusicInfo(
				title = item['title'],
				artist = item['artist'],
				time = sum([a*b for a,b in zip([3600, 60, 1], map(int, item['duration'].split(':')))]),
				image_url = item['image'],
				filepath = os.path.join('https://vk.music7s.cc/', item['url'])
			)
			result.append(mi)
		return result
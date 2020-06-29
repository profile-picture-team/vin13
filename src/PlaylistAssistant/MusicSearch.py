import time
import requests

import logging
logger = logging.getLogger(__name__)

from MusicInfo import MusicInfo

default_image = 'https://img.icons8.com/pastel-glyph/FFFFFF/music-record.png'

session = requests.Session()

def musicSearch(service, q, count = 0):
	"""
		Вызывает функцию поиска для соответствующего сервиса
		Возвращает список объектов MusicInfo
		При ошибке возвращает None
	"""
	service = str(service)
	if service.lower() == 'vk': return musicSearchVK(q, count)
	return None

# https://vk.music7s.cc/api/get_playlist.php?id=
def musicSearchVK(q, count = 0):
	"""
		Отправляет поисковый запрос на vk.music7c.cc
		Возвращает список объектов MusicInfo
		При ошибке возвращает None

		Дата последней проверки апи: 27.05.2020
	"""
	try:
		logger.debug(f'Search request: {q}')
		url = 'https://vk.music7s.cc/api/search.php'
		params = {'search' : q, 'time' : time.time()}
		response = session.get(url, params=params, timeout=10)
		response.raise_for_status()
		data = response.json()
	except requests.Timeout as err:
		logger.error(f'Get: {err.request.url} - Timed out.')
	except requests.HTTPError as err:
		logger.error(f'Get: {err.request.url} - Bad answer: {err.request.status_code}.')
	except requests.ConnectionError as err:
		logger.error(f'Get: {err.request.url} - Connection error')
	except requests.RequestException as err:
		logger.exception(f'Get: {err.request.url} - Unforeseen exception')
	else:
		if data['error']:
			if data['error_message'][:34] != 'Не удалось получить список музыки.':
				logger.warning(f'Get: {response.url} - Error message: {data["error_message"]}')
			return []

		# пакуем полученные данные в MusicInfo
		items = data['items'][:count] if count != 0 else data['items']
		result = list()
		for item in items:
			mi = MusicInfo(
				title = item.get('title'),
				artist = item.get('artist'),
				time = sum([a*b for a,b in zip([3600, 60, 1], map(int, item.get('duration', '0:0:0').split(':')))]),
				image_url = item.get('image'),
				filepath = 'https://vk.music7s.cc' + item['url'] # оставил так, потому что это очень важное поле
			)
			# если отсутствует ссылка на картинку, то устанавливаем ссылку на локальную дефолтную картинку
			if mi.image_url is None:
				mi.image_url = default_image
			result.append(mi)

			# другие названия пересекаются с реальными названиями и именми
			if mi.title is None:  logger.warning(f'{mi.filepath} - Not found title');  mi.title  = 'error'
			if mi.artist is None: logger.warning(f'{mi.filepath} - Not found artist'); mi.artist = 'error'
			if mi.time == 0: logger.warning(f'{mi.filepath} - Music duration is zero')

		return result

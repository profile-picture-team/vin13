import requests
import time
import os
import shutil
import threading
import queue
import re
import json
import logging

from MusicInfo import MusicInfo

logger = logging.getLogger(__name__)


class Downloader:
	"""Класс для многопоточного скачивания файлов и управления ими."""
	def __init__(self, threads = 4, folder = 'music/'):
		logger.info('Creating Downloader...')
		self.ready_files      = set()  # скаченные треки
		self.queuFiles = queue.Queue() # треки для скачивания
		self.processing_files = set()  # скачиваются или есть в очереди
		self.setDowloadFolder(folder, False) # устанавливаем текущую папку загрузок

		self.threads     = list()           # потоки-загрузчики
		self.lockerQueue = threading.Lock() # аналог мьютекса 
		self.stopSignal  = False            # сигнал потокам остановиться
		
		self.eventEmptyQueue = threading.Event()
		self.eventEmptyQueue.clear()

		# загружаем записи о треках в папке
		logger.info('Load objects of MusicInfo')
		filename = os.path.join(self.dowload_folder, 'records.json')
		if os.path.exists(filename):
			logger.info(f'Load from file \'{filename}\'')
			with open(filename, 'r') as f:
				self.ready_files = {MusicInfo.loadFromJSONFormat(mi_dict) for mi_dict in json.load(f)}
		else:
			logger.warning(f'File \'{filename}\' not found')
			self.ready_files = set()

		# удаление записей без файла
		self.deleteLostRecords()
		
		# удаление файлов которых нет в записях
		self.deleteLostFiles()

		# создаём и запускаем потоки
		self.startThreads(threads)

		logger.info('Downloader successfully created')


	def __del__(self):
		self.saveMIRecordsToJson()
		pass


	def fileIsReady(self, mi):
		"""
			Возвращает True если файл есть в списке готовых
			False - в противном случае
		"""
		return mi in self.ready_files


	def getFilePath(self, mi):
		"""
			Возвращет полный путь до файла трека
			Если файл не найдем возвращает None
		"""
		filename = mi.track_id + mi.ext
		file = os.path.join(self.dowload_folder, filename)
		if os.path.exists(file): return file


	def addFileInQueue(self, mi):
		"""
			Добавлет файл в очередь загрузки 
			Если файл уже был скачем или присутствует в очерели,
			то не добавляет
		"""
		if mi in self.ready_files:
			logger.info('File not added to queue: File ready.')
			return
		if mi in self.processing_files:
			logger.info('File not added to queue: File is being processed')
			return
		self.processing_files.add(mi)
		self.queuFiles.put(mi)
		logger.info(f'File with id \'{mi.track_id}\' added in queue')


	def waitAllDownloads(self):
		"""Блокирует поток пока очередь загрузок не станет пустой"""
		logger.debug('Wait event \'Empty queue\'')
		self.eventEmptyQueue.wait()


	def waitFileDowload(self, mi):
		"""Ждет загрузки файла"""
		# TODO: пересадить на события (threading.Event)
		logger.info(f'Wait dowload file with id: {mi.track_id}')
		while mi not in self.ready_files:
			time.sleep(0.01)


	def searchMusic(self, q, count = 0):
		"""
			Отправлет поисковый запрос на сервер
			Возвращает список объектов MusicInfo
			При ошибке возвращает None
		"""
		try:
			logger.info(f'Search request: "{q}"')
			url = 'https://vk.music7s.cc/api/search.php'
			params = {'search' : q, 'time' : time.time()}
			responce = requests.get(url, params=params, timeout=10)
			responce.raise_for_status()
			data = responce.json()
		except requests.Timeout:
			logger.error('Timed out')
		except requests.HTTPError as err:
			logger.error(f'Bad answer: {err.responce.status_code}')
		except requests.ConnectionError:
			logger.error('Connection error')
		except requests.RequestException as err:
			logger.error(f'Unforeseen exception: {err.__class__.__name}: {err}')
		else:
			if data['error']:
				return []

			# пакуем полученные данные в MusicInfo
			items = data['items'][:count] if count != 0 else data['items']
			result = list()
			for item in items:
				mi = MusicInfo(
					track_id = item['url'][12:], # отбросили часть с ссылкой "/get.php?id=XXX_XXX"
					title = item['title'],
					artist = item['artist'],
					image_url = item['image'],
					time = sum([a*b for a,b in zip([3600, 60, 1], map(int, item['duration'].split(':')))])
				)
				result.append(mi)
			return result


	def deleteFile(self, mi):
		"""Удаляет файл и запись о нем"""
		logger.info(f'Delete file with id: {mi.track_id}')
		path = self.getFilePath(mi)
		if path is not None:
			os.remove(path)
		else: logger.warning(f'File \'{path}\' not found')
		if mi in self.ready_files:
			self.ready_files.remove(mi)
		else: logger.warning(f'Record \'{mi.track_id}\' not found')


	def deleteLostRecords(self):
		"""Удаляет записи без файла"""
		# отмечаем записи для удаления, если файл не найден
		logger.info('Marking recoreds for delete...')
		records_for_remove = list()
		for mi in self.ready_files:
			if self.getFilePath(mi) is None:
				# файл не найден
				logger.info(f'Mark \'{mi.track_id}\'')
				records_for_remove.append(mi)

		# удаляем отмеченные записи
		logger.info('Delete marked records...')
		for mi in records_for_remove: self.ready_files.remove(mi)


	def deleteLostFiles(self):
		"""Удаляет файлы треков для которых нет записи"""
		logger.info('Delete lost files...')
		files = next(os.walk(self.dowload_folder))[2] # получаем список файлов в папке 
		for filename in files:
			match = re.search(r'(\d+_\d+)\..+', filename)
			if match is not None:
				track_id = match.group(1)
				if MusicInfo(track_id=track_id) not in self.ready_files:
					logger.info(f'Delete file \'{filename}\'')
					file = os.path.join(self.dowload_folder, filename)
					os.remove(file)


	def setDowloadFolder(self, folder, move_files = True):
		"""Изменяет текущюу папку для файлов хранения фалов"""
		logger.info('Edit dowload folder')
		folder = os.path.abspath(folder)
		if not os.path.exists(folder): os.makedirs(folder)
		if move_files: shutil.move(self.dowload_folder, folder)
		self.dowload_folder = folder


	def startThreads(self, threads = 4):
		logger.info('Runing thread dowloaders...')
		for i in range(threads):
			self.threads.append(
				threading.Thread(
					target = self.targetDownloadThread,
					name   = f'DThread-{i+1}'
				)
			)
			self.threads[-1].start()


	def stopThreads(self):
		"""
			Останавливает и выполняет join потоков-загрузчиков
		"""
		self.stopSignal = True;
		for t in self.threads:
			t.join()
		self.threads = list()


	def targetDownloadThread(self):
		"""Подпрограмма для потока-загрузчика"""
		# TODO: пересадить на события (threading.Event)
		logger.info('Running')
		mi = None
		while not self.stopSignal:
			
			# сюда может зайти только 1 поток
			self.lockerQueue.acquire()
			if not self.queuFiles.empty():
				mi = self.queuFiles.get()
			self.lockerQueue.release()

			if len(self.processing_files) != 0:
				logger.debug('Event \'Empty queue\' locked')
				self.eventEmptyQueue.clear()
			else:
				logger.debug('Event \'Empty queue\' unlocked')
				self.eventEmptyQueue.set()

			if mi is not None:
				try:
					logger.info(f'Download file with id: {mi.track_id}')
					url = 'https://vk.music7s.cc/get.php'
					params = {'id' : mi.track_id}
					responce = requests.get(url, params=params, timeout=10)
					responce.raise_for_status()
				except requests.Timeout:
					logger.error('Timed out')
				except requests.HTTPError as err:
					logger.error(f'Bad answer: {err.responce.status_code}')
				except requests.ConnectionError:
					logger.error('Connection error')
				except requests.RequestException as err:
					logger.error(f'Unforeseen exception: {err.__class__.__name}: {err}')
				else:

					# получаем и записываем расширение файла
					match = re.search(r'filename=".*(\..+)"', responce.headers['Content-Disposition'])
					if match is not None:
						mi.ext = match.group(1)
					else:
						logger.warning('File extension not found')
						mi.ext = ''

					# полный путь до файла
					filename = mi.track_id + mi.ext
					filepath = os.path.join(self.dowload_folder, filename)

					# запись в файл
					logger.info(f'Save to file \'{filepath}\'')
					open(filepath, 'wb').write(responce.content)
					
					# записываем размер файла
					mi.size = len(responce.content)

					# добавляем в список готовых файдов
					self.ready_files.add(mi)
				finally:
					self.processing_files.remove(mi)
					mi = None
			time.sleep(0.01)
		logger.info('Stopped')


	def saveMIRecordsToJson(self):
		filename = os.path.join(self.dowload_folder, 'records.json')
		logger.info(f'Save records to json file \'{filename}\'...')
		with open(filename, 'w') as fp:
			json.dump(list(self.ready_files), fp, default=MusicInfo.toJSONFormat, ensure_ascii=False, indent=4)
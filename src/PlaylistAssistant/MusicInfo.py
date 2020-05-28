class MusicInfo:
	""" Контейнер для хранения информации о треках """
	def __init__(self,
		title     = None,
		artist    = None,
		time      = None,
		image_url = None,
		filepath  = None
	):
		self.title     = title     # название трека
		self.artist    = artist    # исполнитель
		self.time      = time      # длительность в секундах
		self.image_url = image_url # иконка трека
		self.filepath  = filepath  # полный путь до файла

	def isCorrect(mi):
		"""
			Проверяет данные в обекте типа MusicInfo
			Если тип не соответствует или данные не корректны,
			то возвращает False
		"""
		if not isinstance(mi, MusicInfo) or \
		   not isinstance(mi.title, str) or \
		   not isinstance(mi.artist, str) or \
		   not(isinstance(mi.time, int) and mi.time >= 0) or \
		   not isinstance(mi.image_url, str) or \
		   not isinstance(mi.filepath, str) \
		: return False
		return True

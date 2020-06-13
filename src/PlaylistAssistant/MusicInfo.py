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


	def isCorrect(mi) -> bool:
		""" Проверяет данные на корректность в обекте типа MusicInfo """
		return \
			isinstance(mi, MusicInfo) and \
			isinstance(mi.title, str) and \
			isinstance(mi.artist, str) and \
			isinstance(mi.time, int) and \
			isinstance(mi.image_url, str) and \
			isinstance(mi.filepath, str) and \
			mi.time >= 0


	def __eq__(self, other):
		return \
			isinstance(other, MusicInfo) and \
			self.filepath == other.filepath

 
	def __ne__(self, other):
		return not self.__eq__(other)
		
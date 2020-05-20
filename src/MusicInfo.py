"""
	  Created by Ivan Osinin


      _._     _,-'""`-._       QUACK!
     (,-.`._,'(       |\`-/|
         `-.-' \ )-`( , o o)
               `-    \`_`"'-

"""

class MusicInfo:
	""" Контейнер для хранения информации о треках """
	def __init__(self,
		title     = None,
		artist    = None,
		track_id  = None,
		ext       = None,
		time      = None,
		size      = None,
		image_url = None,
		filepath  = None
	):
		self.title     = title     # название трека
		self.artist    = artist    # исполнитель
		self.track_id  = track_id  # id трэка в сервисе
		self.ext       = ext       # расширение файла
		self.time      = time      # длительность в секундах
		self.size      = size      # размер аудио файла в байтах
		self.image_url = image_url # иконка трека
		self.filepath  = filepath  # полный путь до файла

	def __hash__(self):
		return self.track_id.__hash__()

	def __eq__(self, mi):
		if not isinstance(mi, MusicInfo):
			raise TypeError(f"Object of type '{mi.__class__.__name__}', expected '{self.__class__.__name__}'")
		return self.track_id == mi.track_id

	@classmethod
	def loadFromJSONFormat(cls, json_dict):
		"""
			Собирает объект из словаря
			Тип проверяется по атрибуту '__type__',
			если атрибут не равен 'MusicInfo' или не существует,
			то бросает исключение 'TypeError'
		"""
		if not json_dict.get('__type__') == __class__.__name__:
			raise TypeError(f"Expected type '{__class__.__name__}'")
		return cls(
			title     = json_dict['title'],
			artist    = json_dict['artist'],
			track_id  = json_dict['track_id'],
			ext       = json_dict['ext'],
			time      = json_dict['time'],
			size      = json_dict['size'],
			image_url = json_dict['image_url'],
			filepath  = json_dict['filepath']
		)

	# метод для модуля json
	@staticmethod
	def toJSONFormat(mi):
		"""
			Собирает словарь из объекта MusicInfo
			В атрибут '__type__' записывает тип объекта
			Если тип объекта не MusicInfo, то бросает исключение 'TypeError'
		"""
		type_name = mi.__class__.__name__
		if not isinstance(mi, MusicInfo):
			raise TypeError(f"Object of type '{type_name}' is not JSON serializable")
		forJSON = mi.__dict__.copy()
		forJSON['__type__'] = type_name
		return forJSON

import random

from MusicInfo import MusicInfo

class Playlist:

	def __init__(self, *, init_list = list(), loop = False):
		self.record_list = [MusicInfo(el) for el in init_list]
		self.position    = 0
		self.loop        = bool(loop)


	def next(self) -> MusicInfo:
		"""
			Перематывает плейлист вперед
			Возвращает Playlist.getCurrent()
		"""
		self.position += 1
		if self.position >= len(self.record_list):
			if self.loop: self.position = 0
			else: self.position -= 1
		return self.getCurrent()


	def prev(self) -> MusicInfo:
		"""
			Перематывает плейлист назад 
			Возвращает Playlist.getCurrent()
		"""
		self.position -= 1
		if self.position < 0:
			if self.loop: self.position = len(self.record_list) - 1
			else: self.position += 1
		return self.getCurrent()


	def add(self, mi: MusicInfo) -> bool:
		"""
			Если mi нет в списке, то добавляет его в конец
			Возвращает успех операции (True/False)
		"""
		if not MusicInfo.isCorrect(mi): return False
		if mi not in self.record_list:
			self.record_list.append(mi)
			return True
		else: return False


	def delete(self, mi: MusicInfo) -> bool:
		"""
			Удаляет mi из списка
			Возвращает успех операции (True/False)
		"""
		if not mi in self.record_list: return False
		return self.deleteByPosition(self.record_list.index(mi))


	def deleteByPosition(self, pos: int) -> bool:
		"""
			Удаляет элемент списка по индексу
			Бросает TypeError, если isinstance(pos, int) == False
			Возвращает успех операции (True/False)
		"""
		if not isinstance(pos, int): raise TypeError(f'Expected type \'int\', but \'{pos.__class__.__name__}\' was encountered')
		if pos < 0: pos += len(self.record_list)
		if not 0 <= pos < len(self.record_list): return False
		if pos <= self.position: self.position -= 1
		del self.record_list[pos]
		return True


	def deleteAll(self) -> None:
		""" Удаляет все треки из плейлиста и сбрасывает позицию в 0 """
		self.record_list = []
		self.position = 0


	def mix(self) -> None:
		""" Перемешивает плейлист и сбрасывает позицию в 0 """
		random.shuffle(self.record_list)
		self.position = 0


	def getLength(self) -> int:
		""" Возвращает длину плейлиста """
		return len(self.record_list)


	def getPosition(self) -> int:
		""" Возвращает текущую позицию в плейлисте """
		return self.position


	def setPosition(self, pos: int) -> bool:
		"""
			Устанавливает текущую позицию в плейлисте
			Можно использовать отрицательные индексы
			Бросает TypeError, если isinstance(pos, int) == False
			Возвращает успех операции (True/False)
		"""
		if not isinstance(pos, int): raise TypeError(f'Expected type \'int\', but \'{pos.__class__.__name__}\' was encountered')
		if pos < 0: pos = len(self.record_list) + pos
		if not (0 <= pos < len(self.record_list)): return False
		return True


	def getAll(self) -> list: return self.record_list


	def getCurrent(self) -> MusicInfo:
		"""
			Возвращает MusicInfo текущего трека
			Если плейлист пуст, то возвращает None
		"""
		if len(self.record_list) == 0: return None
		return self.record_list[self.position]
		

	def getByPosition(self, pos: int) -> MusicInfo:
		"""
			Возвращает трек по индексу
			Можно использовать отрицательные индексы
			Бросает TypeError, если isinstance(pos, int) == False
			Возвращает успех операции (True/False)
		"""
		if not isinstance(pos, int): raise TypeError(f'Expected type \'int\', but \'{pos.__class__.__name__}\' was encountered')
		if pos < 0: pos = len(self.record_list) + pos
		if not (0 <= pos < len(self.record_list)): return None
		return self.record_list[pos]
		

	def isLoop(self) -> bool: return self.loop


	def setLoop(self, flag: bool) -> None: self.loop = bool(flag)


	def isEnd(self) -> bool: return self.position == len(self.record_list) - 1

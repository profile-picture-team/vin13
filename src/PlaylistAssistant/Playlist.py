import random

from MusicInfo import MusicInfo

class Playlist:

	def __init__(self, *, init_list = list(), loop = False):
		self.record_list = [MusicInfo(el) for el in init_list]
		self.position    = 0
		self.loop        = bool(loop)


	def next(self):
		"""
			Перематывает плейлист вперед и возвращает Playlist.getCurrent()
			В случае ошибки возвращает None (см. Playlist.getCurrent)
		"""
		self.position += 1
		if self.position >= self.getLength():
			if self.loop: self.position = 0
			else: self.position -= 1
		return self.getCurrent()


	def prev(self):
		"""
			Перематывает плейлист назад 
			Возвращает Playlist.getCurrent()
		"""
		self.position -= 1
		if self.position < 0:
			if self.loop: self.position = self.getLength() - 1
			else: self.position += 1
		return self.getCurrent()


	def add(self, mi):
		"""
			Если mi нет в списке, то добавляет его в конец
			Возвращает успех операции (True/False)
		"""
		if not MusicInfo.isCorrect(mi): return False
		if mi not in self.record_list:
			self.record_list.append(mi)
			return True
		else: return False


	def delete(self, mi):
		"""
			Удаляет mi из списка
			Возвращает успех операции (True/False)
		"""
		if not mi in self.record_list: return False
		return self.deleteByPosition(self.record_list.index(mi))


	def deleteByPosition(self, pos: int):
		"""
			Удаляет элемент списка по индексу
			Бросает TypeError, если isinstance(pos, int) == False
			Возвращает успех операции (True/False)
		"""
		if not isinstance(pos, int): raise TypeError(f'Expected type \'int\', but \'{pos.__class__.__name__}\' was encountered')
		if pos < 0: pos += self.getLength()
		if not 0 <= pos < self.getLength(): return False
		if pos <= self.position: self.position -= 1
		del self.record_list[pos]
		return True

	def mix(self):
		""" Перемешивает плейлист и сбрасывает позицию в 0 """
		random.shuffle(self.record_list)
		self.position = 0


	def getLength(self):
		"""	Возвращает длину плейлиста """
		return len(self.record_list)


	def getPosition(self):
		"""	Возвращает текущую позицию в плейлисте """
		return self.position


	def setPosition(self, pos: int):
		"""
			Устанавливает текущую позицию в плейлисте
			Можно использовать отрицательные индексы
			Бросает TypeError, если isinstance(pos, int) == False
			Возвращает успех операции (True/False)
		"""
		if not isinstance(pos, int): raise TypeError(f'Expected type \'int\', but \'{pos.__class__.__name__}\' was encountered')
		if pos < 0: pos = self.getLength() + pos
		if not (0 <= pos < self.getLength()): return False
		return True


	def getAll(self): return self.record_list


	def getCurrent(self):
		"""
			Возвращает MusicInfo текущего трека
			Если плейлист пуст, то возвращает None
		"""
		if self.getLength == 0: return None
		return self.record_list[self.position]
		

	def getByPosition(self, pos: int):
		"""
			Возвращает трек по индексу
			Можно использовать отрицательные индексы
			Бросает TypeError, если isinstance(pos, int) == False
			Возвращает успех операции (True/False)
		"""
		if not isinstance(pos, int): raise TypeError(f'Expected type \'int\', but \'{pos.__class__.__name__}\' was encountered')
		if pos < 0: pos = self.getLength() + pos
		if not (0 <= pos < self.getLength()): return None
		return self.record_list[pos]
		

	def isLoop(self): return self.loop

	def setLoop(self, flag: bool): self.loop = bool(flag)


	def isEnd(self): return self.position == self.getLength() - 1

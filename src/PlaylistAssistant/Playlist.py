import random

from MusicInfo import MusicInfo

class Playlist:

	def __init__(self, init_list = list(), loop = False):
		self.record_list = [MusicInfo(el) for el in init_list]
		self.position    = 0
		self.loop        = bool(loop)


	def next(self):
		if self.loop or self.position < len(self.record_list):
			self.position += 1
			if self.position >= len(self.record_list):
				self.position = 0
			return self.record_list[self.position]
		else: return None


	def prev(self):
		if self.loop or self.position > 0:
			self.position -= 1
			if self.position <= 0:
				self.position = len(self.record_list) - 1
			return self.record_list[self.position]
		else: return None


	def add(self, mi):
		if not MusicInfo.isCorrect(mi): return False
		if mi not in self.record_list:
			self.record_list.append(mi)
			return True
		else: return False


	def delete(self, mi):
		try:
			pos = self.record_list.index(mi)
			return self.deleteByPosition(pos)
		except: return False


	def deleteByPosition(self, pos: int):
		try:
			pos = int(pos)
			# если индекс нисёт негативную энергию, то исправим это
			if pos < 0: pos = self.getLength() + pos
			if not (0 <= pos < self.getLength()): return False
			del self.record_list[pos]
			if pos <= self.position: self.position -= 1
			return True
		except: return False

	def mix(self):
		random.shuffle(self.record_list)
		self.position = 0


	def getLength(self): return len(self.record_list)


	def getPosition(self): return self.position


	def setPosition(self, pos: int):
		try:
			pos = int(pos) % self.getLength()
			if 0 <= pos < self.getLength():
				self.position = pos
				return True
			else: return False
		except: return False


	def getAll(self): return self.record_list


	def getCurrent(self): return self.record_list[self.position]

	def getByPosition(self, pos: int):
		try:
			pos = int(pos)
			return self.record_list[pos]
		except: return None

	def isLoop(self): return self.loop


	def setLoop(self, flag: bool): self.loop = bool(flag)

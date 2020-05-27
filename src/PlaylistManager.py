from Playlist import Playlist

import logging
logger = logging.getLogger(__name__)

class PlaylistManager:

	def __init__(self):
		self.playlists = dict()

	def getPlalist(self, pl_id):
		"""
			Возвращает плейлист по id
			Бросает KeyError, если плейлист не существует
		"""
		return self.playlists[pl_id]

	def newPlaylist(self, pl_id):
		""" Создаёт новый плейлист, удаляя старый """
		self.delPlaylist(pl_id)
		logger.debug(f'New Playlist with id: {pl_id}')
		self.playlists[pl_id] = Playlist()

	def delPlaylist(self, pl_id):
		""" Удаляет плейлист, если он существует """
		if self.isExistPlaylist(pl_id):
			logger.debug(f'Delete Playlist with id: {pl_id}')
			del self.playlists[pl_id]

	def isExistPlaylist(self, pl_id): return pl_id in self.playlists 

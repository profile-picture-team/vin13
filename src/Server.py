
import asyncio
import threading
import logging
import discord

logger = logging.getLogger(__name__)

Server_loop = asyncio.get_event_loop()
#discord server (guild)
class Server:

	generate_embed = lambda mi: discord.Embed()

	def __init__(self, ctx, voice = None, playlist = None):
		self.ctx = ctx
		self.voice = voice
		self.playlist = playlist
		
		self.eventNextTrack = threading.Event()
		self.eventStartLoop = threading.Event()
		self.stopSignal = False

		self.playing_thread = threading.Thread(target = self.playlistLoop)
		self.playing_thread.start()


	def playlistLoop(self):
		server_id = self.ctx.guild.id
		logger.info(f'Server: {server_id}. Start playing thread: {threading.current_thread().getName()}')

		def my_after(error):
			self.eventNextTrack.set()

		while not self.stopSignal:
			self.eventStartLoop.wait()

			logger.debug(f'Server: {server_id}. Start loop')
			while not self.stopSignal and self.playlist.getLength() > 0 and self.voice.is_connected():
				mi = self.playlist.next()
				self.eventNextTrack.clear()
				self.voice.play(discord.FFmpegOpusAudio(mi.filepath), after=my_after)
				asyncio.run_coroutine_threadsafe(self.ctx.send(embed = Server.generate_embed(mi)), Server_loop).result()
				self.eventNextTrack.wait()
				logger.debug(f'Server: {server_id}. Next track')
			logger.debug(f'Server: {server_id}. Stop loop')
			
			self.eventStartLoop.clear()
		logger.info(f'Server: {server_id}. Playing thread died')
		

	def start(self):
		self.eventStartLoop.set()
		self.voice.resume()


	def stop(self):
		server_id = self.ctx.guild.id
		logger.info(f'Server: {server_id}. Stop signal')
		self.stopSignal = True
		self.eventNextTrack.set()
		self.eventStartLoop.set()



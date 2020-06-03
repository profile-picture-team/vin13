
import asyncio
import threading
import logging
import discord

logger = logging.getLogger(__name__)

Server_loop = asyncio.get_event_loop()
#discord server (guild)
class Server:

	generate_embed = lambda mi: discord.Embed()

	def __init__(self, ctx = None, voice = None, playlist = None):
		self.ctx = ctx
		self.voice = voice
		self.playlist = playlist
		self.eventNextTrack = threading.Event()

		self.playing_thread = threading.Thread(target = self.target)

	def target(self):
		server_id = self.ctx.message.guild.id
		logger.debug(f'Server: {server_id}. Start playing thread: {threading.current_thread().getName()}')

		def my_after(error):
			self.eventNextTrack.set()

		logger.debug(f'Server: {server_id}. Start loop')
		while self.playlist.getLength() > 0 and self.voice.is_connected():
			mi = self.playlist.next()
			self.eventNextTrack.clear()
			self.voice.play(discord.FFmpegOpusAudio(mi.filepath), after=my_after)
			send_fut = asyncio.run_coroutine_threadsafe(self.ctx.send(embed = Server.generate_embed(mi)), Server_loop)
			send_fut.result()
			self.eventNextTrack.wait()
			logger.debug(f'Server: {server_id}. Next track')
		logger.debug(f'Server: {server_id}. Stop loop')
		self.loop_started = False

	def start(self):
		if not self.playing_thread.is_alive() and self.playlist.getLength() > 0:
			self.playing_thread.start()


import asyncio
import threading
import logging
import discord

logger = logging.getLogger(__name__)

Channel_loop = asyncio.get_event_loop()
class Channel:

	generate_embed = lambda mi: discord.Embed()

	def __init__(self, ctx = None, voice = None, playlist = None):
		self.ctx = ctx
		self.voice = voice
		self.playlist = playlist
		self.eventNextTrack = threading.Event()

		self.playing_thread = threading.Thread(target = self.target)

	def target(self):
		channel_id = self.ctx.message.guild.id
		logger.debug(f'Channel: {channel_id}. Start playing thread with name: {threading.current_thread().getName()}')		

		def my_after(error):
			self.eventNextTrack.set()

		logger.debug(f'Channel: {channel_id}. Start loop')
		while self.playlist.getLength() > 0 and self.voice.is_connected():
			mi = self.playlist.next()
			self.eventNextTrack.clear()
			self.voice.play(discord.FFmpegPCMAudio(mi.filepath), after=my_after)
			send_fut = asyncio.run_coroutine_threadsafe(self.ctx.send(embed = Channel.generate_embed(mi)), Channel_loop)
			send_fut.result()
			#asyncio.run(self.ctx.send(embed=get_mi_embed(mi)))
			#сука как
			self.eventNextTrack.wait()
			logger.debug(f'Channel: {channel_id}. Next track')
		logger.debug(f'Channel: {channel_id}. Stop loop')
		self.loop_started = False

	def start(self):
		if not self.playing_thread.is_alive() and self.playlist.getLength() > 0:
			self.playing_thread.start()
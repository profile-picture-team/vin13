import  discord
from discord.ext import commands
from discord.utils import get

import os, sys
import requests
import time
import asyncio

import logging
import logging.config

logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger(__name__)
logger.info('Program start')

from PlaylistAssistant.PlaylistManager import PlaylistManager
import PlaylistAssistant.MusicSearch as MS
from PlaylistAssistant.MusicInfo import MusicInfo

PM = PlaylistManager()

pl_img = 'https://img.icons8.com/pastel-glyph/2x/search--v2.png'

def Bot():
	voices = {}
	client = commands.Bot(command_prefix=os.getenv('PREFIX'), case_insensitive=True)

	global client_loop
	client_loop = asyncio.get_event_loop()

	def get_mi_embed(mi):
		emb = discord.Embed(colour = 0x007D80)
		emb.set_author(name = f'{mi.artist} - {mi.title} [ {mi.time} сек ]', icon_url = mi.image_url)
		return emb

	@client.event
	async def on_ready():
		await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="aplha ver."))
		logger.info('Bot ready')
		# client.remove_command('help')

	@client.command(pass_context = True)
	async def join(ctx):
		try:
			channel = ctx.message.author.voice.channel
		except:
			await ctx.send('Присоединись к каналу, мудак')
			return False

		voice = get(client.voice_clients, guild = ctx.guild)

		if voice and voice.is_connected():
			await voice.move_to(channel)
		else:
			voice = await channel.connect()
			await ctx.send(embed = discord.Embed(description=f':white_check_mark: Бот подключился к каналу {channel}', colour = 0x007D80))
		voices[ctx.message.guild.id] = voice
		return True
		# await ctx.send(f'бот присоединился к каналу: {channel}')

	@client.command()
	async def leave(ctx):
		voice = get(client.voice_clients, guild = ctx.guild)
		if voice and voice.is_connected():
			await voice.disconnect()
			await ctx.send(embed = discord.Embed(description=':no_entry: Бот отключился', colour = 0x007D80))
		else:
			await ctx.send('А как какать?')

	@client.command()
	async def play(ctx, *args):
		if await join(ctx) == False:
			return
		song_q = " ".join(args[:])
		pl_id = ctx.message.guild.id
		voice = voices[pl_id]

		if voice.is_paused():
			voice.resume()

		if not PM.isExistPlaylist(pl_id):
			PM.newPlaylist(pl_id)
		pl = PM.getPlaylist(pl_id)

		if song_q:
			mi = MS.musicSearch('vk', song_q, 1)
			if not mi:
				await ctx.send('Ошибка поиска!')
				return
			mi = mi[0]

			if pl.add(mi) == True:
				await ctx.send(f'Добавил: {mi.artist} - {mi.title}')
			else:
				await ctx.send('Ошибка добавления!')
				return

		# мб потом добавлю отпраление сообщения, что начал играть песню
		if not voice.is_playing() and pl.getLength() > 0:
			def my_after(error):
				if pl.getLength() > 0:
					pl.next()
					if voice.is_connected():
						mic = pl.getCurrent()
						voice.play(discord.FFmpegPCMAudio(mic.filepath), after=my_after)
						send_fut = asyncio.run_coroutine_threadsafe(ctx.send(embed = get_mi_embed(mic)), client_loop)
						send_fut.result()

			mic = pl.getCurrent()
			voice.play(discord.FFmpegPCMAudio(mic.filepath), after=my_after)
			await ctx.send(embed = get_mi_embed(mic))

	@client.command()
	async def skip(ctx):
		try:
			voice = voices[ctx.message.guild.id] # я знаю про ctx.message.guild.id in voices, но мне лень
		except:
			return
		voice.stop()

	@client.command()
	async def playing(ctx):
		pl_id = ctx.message.guild.id
		if PM.isExistPlaylist(pl_id):
			pl = PM.getPlaylist(pl_id)
			if pl.getLength() > 0:
				mic = pl.getCurrent()
				await ctx.send(embed = get_mi_embed(mic))
				#await ctx.send(f'Сейчас играет: {mi.artist} - {mi.title}')

	@client.command()
	async def pause(ctx):
		try:
			voice = voices[ctx.message.guild.id] # я знаю про ctx.message.guild.id in voices, но мне лень
		except:
			return
		if voice and voice.is_playing():
			voice.pause()

	@client.command()
	async def remove(ctx, id_to_remove: int):
		try:
			voice = voices[ctx.message.guild.id] # я знаю про ctx.message.guild.id in voices, но мне лень
		except:
			return
		pl_id = ctx.message.guild.id
		if PM.isExistPlaylist(pl_id):
			pl = PM.getPlaylist(pl_id)
			if pl.getLength() > 0:
				mi = pl.getByPosition(id_to_remove)
				if mi:
					old_main_pos = pl.getPosition()
					if pl.deleteByPosition(id_to_remove):
						await ctx.send(f'Удалил: {mi.artist} - {mi.title} :fire:')
					if old_main_pos == id_to_remove:
						voice.stop() #await skip(ctx)

	@remove.error
	async def remove_error(ctx, error):
		await ctx.send('Ты кто такой, сука, чтоб это делать?')

	@client.command()
	async def queue(ctx):
		pl_id = ctx.message.guild.id
		if PM.isExistPlaylist(pl_id):
			pl = PM.getPlaylist(pl_id)
			mis = pl.getAll()
			if len(mis) > 0:
				to_send = str()
				curr_id = pl.getPosition()
				for i in range(0, curr_id):
					to_send = to_send + f'{i} :  {mis[i].artist} - {mis[i].title}\n'
				to_send = to_send + f' -> {curr_id} :  {mis[curr_id].artist} - {mis[curr_id].title}\n'
				for i in range(curr_id + 1, len(mis)):
					to_send = to_send + f'{i} :  {mis[i].artist} - {mis[i].title}\n'
				emb = discord.Embed(title='', description=to_send, color=0x007D80)
				emb.set_author(name = 'текущий плейлист', icon_url = pl_img)

				await ctx.send(embed = emb)
			else:
				await ctx.send('Плейлист пуст')
		else:
			await ctx.send('Плейлист не создан')

	client.run(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
	try:
		Bot()
	except KeyboardInterrupt:
		logger.warning('Interrupted')
	except Exception as error:
		logger.exception(error)
	logger.info('Program end.\n')
	sys.exit(0)

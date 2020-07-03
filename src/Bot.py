import discord
from discord.ext import commands

import os
import asyncio
from urllib.parse import urlparse

import logging
logger = logging.getLogger(__name__)

from PlaylistAssistant import *
from Server import Server
from GenEmbed import MsgEmbed

# Жму F за всех кому надо работать с этим кодом


#region var

icons = {
	'playlist' : 'https://img.icons8.com/pastel-glyph/FFFFFF/playlist.png',
	'search'   : 'https://img.icons8.com/pastel-glyph/FFFFFF/search--v2.png',
	'list'     : 'https://img.icons8.com/windows/96/FFFFFF/untested.png'
}

servers = dict() # id : Server.Server

client = commands.Bot(command_prefix=os.getenv('PREFIX'), case_insensitive=True)
client.remove_command('help')

#endregion

#region get_server/mi_embed, join_to_channel

def get_server(ctx) -> Server:
	"""
		Возвращает Server из servers
		Если нет экземпляра, то создаёт его
	"""
	server_id = ctx.guild.id
	if server_id in servers:
		return servers[server_id]
	else:
		server = Server(ctx=ctx, playlist=Playlist(loop=True))
		servers[server_id] = server
		return server
		

def get_mi_embed(mi):
	emb = MsgEmbed.info('')
	emb.set_author(name = f'{mi.artist} - {mi.title} [ {mi.time} сек ]', icon_url = mi.image_url)
	return emb
Server.generate_embed = get_mi_embed


async def join_to_channel(ctx, channel):
	"""
		Подключает бота к каналу
		return 0 - всё ок
		return 1 - бот уже подключен к этому каналу
		return 2 - боту не удалось подключится (см. логи)
	"""
	server_id = ctx.guild.id
	logger.debug(f'Server: {server_id}. Joining to channel...')

	# Мне накакать, что в питоне не принято юзать коды возврата
	try:
		server = get_server(ctx)
		if server.voice is None:
			server.voice = await channel.connect()
			logger.debug(f'Server: {server_id}. Joined \'{channel}:{channel.position}\'')
		elif server.voice.is_connected():
			if server.voice.channel == channel:
				logger.debug(f'Server: {server_id}. Join error: Already joined')
				return 1
			await server.voice.move_to(channel)
			logger.debug(f'Server: {server_id}. Joined \'{channel}:{channel.position}\'')
		else:
			# Я не знаю как подключить уже существующий войс, если это вообще возможно -_-
		    # ... (читаю твои коменты и мне становится плохо)
			server.voice = await channel.connect()
			logger.debug(f'Server: {server_id}. Joined \'{channel}:{channel.position}\'')
	except:
		logger.exception(f'Server: {server_id}. Join error: unknown')
		return 2
	return 0

#endregion

#region @client.events

@client.event
async def on_ready():
	await client.change_presence(
		status=discord.Status.online,
		activity=discord.Activity(
			type=discord.ActivityType.watching,
			name="hentai"
		)
	)
	logger.info('Bot ready')

@client.event
async def on_error(event, ctx, *args, **kwargs):
	logger.exception(f'Exception in on_error. Event: {event}')
	await ctx.send(embed=MsgEmbed.error('!!! ОШИБКА !!!'))

@client.event
async def on_command(ctx):
	server_id = ctx.guild.id
	logger.debug(f'Server: {server_id}. Command: {ctx.command} {ctx.args[1:]}')
	

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send(embed=MsgEmbed.error('Не дорос ещё!'))
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send(embed=MsgEmbed.error(f'Такой команды нет! `{ctx.prefix}help` - для справки'))
	elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
		await ctx.send(embed=MsgEmbed.error(f'Глаза разуй! Такого аргумента нет! `{ctx.prefix}help {ctx.command}` - для справки'))
	else:
		raise error

#endregion

#region @client.command

@client.command(name='help')
async def _help(ctx, cmd=''):
	if cmd == '':
		await ctx.send(help_docs['main-page'])
	elif cmd == 'not-exist':
		await ctx.send(help_docs['commands']['not-exist'].format(cmd=cmd))
	elif cmd in help_docs['commands']:
		await ctx.send(help_docs['commands'][cmd])
	else:
		await ctx.send(help_docs['commands']['not-exist'].format(cmd=cmd))


@client.command()
async def join(ctx, channel_name = '', *, reconnect = True):
	server_id = ctx.guild.id
	
	if not reconnect:
		voice = get_server(ctx).voice
		if voice and voice.is_connected(): return True

	# получаем канал для подключения (или вылетаем с ошибкой)
	if channel_name == '':
		if ctx.author.voice is None:
			logger.debug(f'Server: {server_id}. Join error: User is not connected')
			await ctx.send(embed=MsgEmbed.error('Присоединись к каналу, мудак'))
			return False
		channel = ctx.author.voice.channel
	else:
		channels = list(filter(lambda x: x.name==channel_name, ctx.guild.voice_channels))
		if len(channels) == 0:
			logger.debug(f'Server: {server_id}. Join error: Channel not found')
			await ctx.send(embed=MsgEmbed.error('Ты инвалид? Название канала неправильное'))
			return False
		elif len(channels) == 1: channel = channels[0]
		else:
			# составляем список каналов и отправляем его
			_list = [f'{i + 1} :  {x} ({x.position + 1}-й)\n' for i,x in enumerate(channels)]
			emb = MsgEmbed.info(''.join(['0. Отмена\n'] + _list))
			emb.set_author(name = 'выберите канал', icon_url = icons['list'])
			await ctx.send(embed = emb)
			
			def get_message_check(author):
				def is_message_correct(message):
					return message.author == author and message.content.isdigit()
				return is_message_correct

			# обрабатываем ответ пользователя
			try:
				# ждем пока автор ответит числом
				msg = await client.wait_for('message', check=get_message_check(ctx.author), timeout=10)
				index = int(msg.content)

				if index == 0:
					logger.debug(f'Server: {server_id}. Joining canceled')
					await ctx.send(embed=MsgEmbed.warning('Подключение отменено'))
					return False
				if index > len(channels):
					await ctx.send(embed=MsgEmbed.warning('Пользователь дурак. Подключение отменено'))
					return False
				channel = channels[index - 1]
			except asyncio.exceptions.TimeoutError:
				logger.debug(f'Server: {server_id}. Join error: User answer timeout')
				await ctx.send(embed=MsgEmbed.warning('Время вышло. Подключение отменено'))
				return False
			

	result = await join_to_channel(ctx, channel)
	if result == 0: await ctx.send(embed=MsgEmbed.ok(f'Бот подключился к каналу: {channel}'))
	elif result == 1: await ctx.send(embed=MsgEmbed.warning(f'Бот уже подключен к каналу: {channel}'))
	elif result == 2: await ctx.send(embed=MsgEmbed.error(f'Ты че наделал?'))
	else: await ctx.send(embed=MsgEmbed.error('Ничего не понял, но очень интересно'))

	# Я не хачу пихать return в if'ы, что бы не нарушать гармонию форматирования
	return 0 <= result <= 1


@client.command()
async def leave(ctx):
	voice = get_server(ctx).voice
	if voice and voice.is_connected():
		await voice.disconnect()
		await ctx.send(embed=MsgEmbed.warning('Бот отключился'))
	else:
		await ctx.send(embed=MsgEmbed.error('Этим можно просто брать и обмазываться'))
	

@client.command()
async def play(ctx, *args):
	if len(args) == 0 or await add(ctx, *args):
		if await join(ctx, reconnect = False): get_server(ctx).start()


@client.command()
async def pause(ctx):
	voice = get_server(ctx).voice
	if voice: voice.pause()


@client.command()
async def skip(ctx, count: int = 1):
	server_id = ctx.guild.id
	if server_id in servers:
		server = servers[server_id]
		if server.playlist.getLength() == 0:
			await ctx.send(embed=MsgEmbed.error('Скипалка не отросла'))
			return
		for i in range(count - 1):
			server.playlist.next()
		server.voice.stop()
	else:
		await ctx.send(embed=MsgEmbed.error('Может ты плейлист создашь прежде чем скипать?'))


@client.command()
async def add(ctx, *args):
	server = get_server(ctx)

	if len(args) == 0:
		await ctx.send(embed=MsgEmbed.error("Недосдача по аргументам, жмот"))
		return False


	if args[0] == '--id':
		if len(args) < 2:
			await ctx.send(embed=MsgEmbed.error("Недосдача по аргументам, жмот"))
			return False
		if len(args) > 2:
			await ctx.send(embed=MsgEmbed.warning("Слишком много аргументов"))
		mi_list = VkSearch.byPlaylistId(args[1])
		isPlaylist = True
	elif VkSearch.isCorrectPlaylistUrl(args[0]):
		if len(args) > 1:
			await ctx.send(embed=MsgEmbed.warning("Слишком много аргументов"))
		mi_list = VkSearch.byPlaylistUrl(args[0])
		isPlaylist = True
	else:
		mi_list = VkSearch.byString(' '.join(args), 5)
		isPlaylist = False
	
	
	if mi_list is None: await ctx.send(embed=MsgEmbed.error('Ошибка поиска!')); return False
	if mi_list == []: await ctx.send(embed=MsgEmbed.warning('Ничего не найдено!')); return False

	def get_message_check(author):
		def is_message_correct(message):
			return message.author == author and message.content.isdigit()
		return is_message_correct

	async def askSingleorFull():
		emb = MsgEmbed.info('\n0. Отмена\n1. Одна песня\n2. Весь плейлист')
		emb.set_author(name = 'выберите тип загрузки', icon_url = icons['list'])
		await ctx.send(embed = emb)

		try:
			msg = await client.wait_for('message', check=get_message_check(ctx.author), timeout=10)
			index = int(msg.content)
			if index == 0: await ctx.send(embed=MsgEmbed.warning('Отменено')); return
			elif index == 1: return True
			elif index == 2: return False
			else: await ctx.send(embed=MsgEmbed.error('Ты кто такой, сука, чтоб это делать?')); return
		except asyncio.exceptions.TimeoutError:
			await ctx.send(embed=MsgEmbed.warning('Кто не успел - тот опоздал'))
			return

	if isPlaylist: user_pl_ans = await askSingleorFull()
    
	if not isPlaylist or user_pl_ans:
		# генерируем и отправляем список треков
		_list = [f'{i + 1} :  {mi.artist} - {mi.title}' for i,mi in enumerate(mi_list)]
		emb = MsgEmbed.info('\n'.join(['0. Отмена'] + _list))
		emb.set_author(name = 'выберите песню', icon_url = icons['search'])
		await ctx.send(embed = emb)

		# ждём от пользователя индекс трека
		try:
			msg = await client.wait_for('message', check=get_message_check(ctx.author), timeout=10)
			index = int(msg.content)
			if index == 0:
				await ctx.send(embed=MsgEmbed.warning('Отменено'))
				return False
			index -= 1
			if 0 <= index < len(mi_list): mi = mi_list[index]
			else: await ctx.send(embed=MsgEmbed.error('Ты кто такой, сука, чтоб это делать?')); return False
		except asyncio.exceptions.TimeoutError:
			await ctx.send(embed=MsgEmbed.warning('Кто не успел - тот опоздал'))
			return False

		# пытаемся добавить трек в плейлист
		if server.playlist.add(mi): await ctx.send(embed=MsgEmbed.info(f'Добавил: {mi.artist} - {mi.title}'))
		else: await ctx.send(embed=MsgEmbed.error('Ошибка добавления!')); return False
	elif user_pl_ans is None:
		return False
	else:
		added_songs = 0
		songs_count = len(mi_list)
		for mi in mi_list:
			if server.playlist.add(mi): added_songs += 1; await ctx.send(embed=MsgEmbed.info(f'Добавил: {mi.artist} - {mi.title}'))
			else: await ctx.send(embed=MsgEmbed.error(f'Не удалось добавить: {mi.artist} - {mi.title}'))
		if added_songs == songs_count:
			await ctx.send(embed=MsgEmbed.ok('Все песни успешно добавлены!'))
		elif added_songs == 0:
			await ctx.send(embed=MsgEmbed.error('Ни одна песня не была добавлена!')); return False
		else:
			await ctx.send(embed=MsgEmbed.info(f'Добавлено {added_songs} песен(я/и)'))

	return True


@client.command()
async def remove(ctx, arg):
	server = get_server(ctx)

	if arg == 'all':
		server.playlist.deleteAll()
		if server.voice: server.voice.stop()
		await ctx.send(embed=MsgEmbed.info('Удалил весь плейлист :fire:'))
		return
	
	if not arg.isdigit(): raise commands.MissingRequiredArgument()
	else: pos = int(arg)

	if not 0 <= pos < server.playlist.getLength():
		await ctx.send(embed=MsgEmbed.error('Как может в казино быть колода разложена в другом порядке?! Ты чё, бредишь, что ли?! Ёбаный твой рот, а!..'))
		return
	
	mi = server.playlist.getByPosition(pos)
	playlist, voice = server.playlist, server.voice
	if pos == playlist.getPosition() and voice: voice.stop()
	if playlist.deleteByPosition(pos): await ctx.send(embed=MsgEmbed.info(f'Удалил: {mi.artist} - {mi.title} :fire:'))
	else: await ctx.send(embed=MsgEmbed.error('Ошибка удаления'))


@client.command()
async def playing(ctx):
	playlist = get_server(ctx).playlist
	if playlist.getLength() == 0:
		await ctx.send(embed=MsgEmbed.warning('Плейлист пуст'))
		return
	await ctx.send(embed=get_mi_embed(playlist.getCurrent()))


@client.command()
async def queue(ctx):
	server = get_server(ctx)

	if server.playlist.getLength() == 0:
		emb = MsgEmbed.info('Плейлист пуст')
	else:
		mi_list = server.playlist.getAll()
		_list = [f'{i} :  {mi.artist} - {mi.title}' for i,mi in enumerate(mi_list)]
		pos = server.playlist.getPosition()
		_list[pos] = f'**{_list[pos]}**'
		emb = MsgEmbed.info('\n'.join(_list))

	emb.set_author(name = 'текущий плейлист', icon_url = icons['playlist'])
	await ctx.send(embed = emb)


@client.command()
async def about(ctx):
	await ctx.send(embed=MsgEmbed.info(about_docs))
	pass	

#endregion

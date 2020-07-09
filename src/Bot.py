import discord
from discord.ext import commands

import os
import asyncio
from typing import *

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

#region utility


def member_is_connected(member: discord.Member, voice_channel: discord.VoiceChannel = None) -> bool:
	if voice_channel is None: return member.voice
	else: return member.voice and member.voice.channel == voice_channel


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


def get_message_check(author):
	def is_message_correct(message):
		return message.author == author and message.content.isdigit()
	return is_message_correct


def get_mi_embed(mi: MusicInfo) -> discord.Embed:
	emb = MsgEmbed.info('')
	emb.set_author(name = f'{mi.artist} - {mi.title} [ {mi.time} сек ]', icon_url = mi.image_url)
	return emb
Server.generate_embed = get_mi_embed


async def ask_user(
	ctx,
	title: str, choice: List[str],
	*, icon_url: str = icons['list'],
	timeout = 10,
	start_index = 0, step_index = 1
) -> Optional[int]:
	choice = [f'{i + start_index}. {x}' for i, x in enumerate(choice)]
	emb = MsgEmbed.info('')
	emb.set_author(name = title, icon_url = icon_url)
	await send_long_list(ctx, choice, emb, MsgEmbed.info(''))
	try:
		msg = await client.wait_for('message', check=get_message_check(ctx.author), timeout=timeout)
	except asyncio.exceptions.TimeoutError:
		await ctx.send(embed=MsgEmbed.warning('Кто не успел - тот опоздал'))
		return None
	else:
		return int(msg.content)


async def join_to_channel(ctx, channel) -> int:
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
	server.ctx = ctx
	return 0


async def send_long_list(ctx, items, first_embed: discord.Embed, last_embed: discord.Embed):
	""" Отправляет длинный список строк в нескольких discord.Embed """
	def chunks(l, n):
		"""Yield successive n-sized chunks from l."""
		"""Ctrl+C Ctrl+V"""
		for i in range(0, len(l), n):
			yield l[i:i + n]
	_chunks = list(chunks(items, 30))
	
	if len(_chunks) >= 1:
		embed = first_embed
		embed.description = '\n'.join(_chunks[0])
		await ctx.send(embed=embed)
	if len(_chunks) >= 3:
		embed = discord.Embed(colour=embed.colour)
		for chunk in _chunks[1:-1]:
			embed.description = '\n'.join(chunk)
			await ctx.send(embed=embed)
	if len(_chunks) >= 2:
		embed = last_embed
		embed.description = '\n'.join(_chunks[-1])
		await ctx.send(embed=embed)

#endregion

#region @client.events

@client.event
async def on_ready():
	await client.change_presence(
		status=discord.Status.online,
		activity=discord.Activity(
			type=discord.ActivityType.watching,
			name="futa on hanime"
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

@client.event
async def on_voice_state_update(member, before, after):
	before_channel = before.channel
	after_channel = after.channel
	if before_channel is None: return
	if after_channel is not None and before_channel.id == after_channel.id: return
	sid = before_channel.guild.id
	if not sid in servers: return
	server = servers[sid]
	voice = server.voice
	if voice is None: return
	bot_id = client.user.id
	before_members = before_channel.members
	if len(before_members) != 1 or before_members[0].bot == True and before_members[0].id != bot_id: return
	if len(voice.channel.members) > 1: return
	if after_channel and after_channel.members[0].id == bot_id: 
		await voice.move_to(before_channel)
		await server.ctx.send(embed = MsgEmbed.hearts('Не надо стесняться'))
		return
	if voice.channel.id != before_channel.id: return
	if voice.is_connected(): 
		if after_channel is None:
			await voice.disconnect()
			await server.ctx.send(embed = MsgEmbed.hearts('Пока-пока'))
		else: 
			await voice.move_to(after.channel)
			await server.ctx.send(embed = MsgEmbed.hearts(f'Ты куда, {after_channel.members[0].mention}?'))

#endregion

#region @client.command

@client.command(name='help', aliases=['h'])
async def _help(ctx, cmd=''):
	if cmd == '':
		await ctx.send(help_docs['main-page'])
	elif cmd == 'not-exist':
		await ctx.send(help_docs['commands']['not-exist'].format(cmd=cmd))
	elif cmd in help_docs['commands']:
		await ctx.send(help_docs['commands'][cmd])
	else:
		await ctx.send(help_docs['commands']['not-exist'].format(cmd=cmd))


@client.command(aliases=['j'])
async def join(ctx, channel_name='', *, reconnect = True) -> bool:
	
	async def get_voice_channel() -> Optional[discord.VoiceChannel]:
		if channel_name == '':
			if not member_is_connected(ctx.author):
				await ctx.send(embed=MsgEmbed.error('Присоединись к каналу, мудак'))
				return None	
			return ctx.author.voice.channel
		return get_voice_channel_by_name() 

	async def get_voice_channel_by_name() -> Optional[discord.VoiceChannel]:
		channels = list(filter(lambda x: x.name == channel_name, ctx.guild.voice_channels))
		if len(channels) == 0:
			await ctx.send(embed=MsgEmbed.error('Ты инвалид? Название канала неправильное'))
			return None
		elif len(channels) == 1: return channels[0]
		else:
			choice = [f' {x} ({x.position + 1}-й)\n' for x in channels]
			choice.insert(0, 'Отмена')
			answer = await ask_user(ctx, 'выбери канал', choice, icon_url = icons['list'])
			if answer is None: return None
			if answer == 0:
				await ctx.send(embed=MsgEmbed.warning('Подключение отменено'))
				return None
			if 1 <= answer <= len(channels):
				return channels[answer - 1]
			await ctx.send(embed=MsgEmbed.warning('Ты кто такой, сука, чтоб это делать?'))
			return None


	if not reconnect:
		voice = get_server(ctx).voice
		if voice and voice.is_connected(): return True
	
	channel = await get_voice_channel()
	if channel is None: return False

	result = await join_to_channel(ctx, channel)
	if result == 0:	await ctx.send(embed=MsgEmbed.ok(f'Бот подключился к каналу: {channel}'))
	elif result == 1: await ctx.send(embed=MsgEmbed.warning(f'Бот уже подключен к каналу: {channel}'))
	elif result == 2: await ctx.send(embed=MsgEmbed.error(f'Ты че наделал?'))
	else: await ctx.send(embed=MsgEmbed.error('Ничего не понял, но очень интересно'))

	# Я не хачу пихать return в if'ы, что бы не нарушать гармонию форматирования
	return 0 <= result <= 1


@client.command(aliases=['l'])
async def leave(ctx):
	voice = get_server(ctx).voice
	if voice and voice.is_connected():
		await voice.disconnect()
		await ctx.send(embed=MsgEmbed.warning('Бот отключился'))
	else:
		await ctx.send(embed=MsgEmbed.warning('Этим можно просто брать и обмазываться'))
	

@client.command(aliases=['p'])
async def play(ctx, *args):
	if len(args) == 0 or await add(ctx, *args):
		if await join(ctx, reconnect = False):
			server = get_server(ctx)
			server.playlist.prev()
			server.start()


@client.command(aliases=['pa'])
async def pause(ctx):
	voice = get_server(ctx).voice
	if voice: voice.pause()


@client.command(aliases=['s'])
async def skip(ctx, count: int = 1):
	server = get_server(ctx)
	voice = server.voice
	playlist = server.playlist
	if playlist.getLength() == 0:
		await ctx.send(embed=MsgEmbed.warning('Скипалка не отросла'))
		return
	for i in range(count - 1):
		playlist.next()
	if voice:
		voice.stop()
	

@client.command(aliases=['a'])
async def add(ctx, *args) -> Optional[bool]:
	"""
		Добавляет в плейлист сервера новые треки
		
		args == ['--id', '...'] - поиск плейлиста по id
		args == ['url'] - поиск плейлиста по ссылке
		args == [...] - поиск трека по ключевым словам

		return True  - в плейлист был добавлен хотя бы 1 трек
		return False - в плейлист не было ничего добавлено
		return None  - таймаут, некорректные данные пользователя, ошибка апи
	"""

	async def cancel():
		await ctx.send(embed=MsgEmbed.warning('Отменено'))
		return False

	async def bad_answer():
		await ctx.send(embed=MsgEmbed.warning('Ты кто такой, сука, чтоб это делать?'))
		return None

	async def add_all():
		added_songs, songs_count = 0, len(mi_list)
		message = await ctx.send(embed=MsgEmbed.info('Загрузка плейлиста...'))
		for mi in mi_list:
			if server.playlist.add(mi): added_songs += 1
		if added_songs == songs_count:
			await message.edit(embed=MsgEmbed.ok('Все песни успешно добавлены!'))
			return True
		elif added_songs == 0:
			await message.edit(embed=MsgEmbed.warning('Ни одна песня не была добавлена!'))
			return False
		else:
			await message.edit(embed=MsgEmbed.warning(f'Добавлено: {added_songs}/{songs_count}'))
			return True

	async def add_one():
		songs_list = [f' {mi.artist} - {mi.title}' for mi in mi_list]
		songs_list.insert(0, 'Отмена')
		answer = await ask_user(ctx, 'выбери песню', songs_list, icon_url = icons['search'])
		if answer is None: return None
		if answer == 0: return await cancel()
		if 1 <= answer <= len(mi_list): mi = mi_list[answer - 1]
		else: return bad_answer()
		if server.playlist.add(mi): await ctx.send(embed=MsgEmbed.ok(f'Добавил: {mi.artist} - {mi.title}'))
		else: await ctx.send(embed=MsgEmbed.error('Ошибка добавления!'))

	async def load_playlist():
		method = {
			0 : cancel,
			1 : add_one,
			2 : add_all,
			None : lambda: None
		}.get(await ask_user(ctx, 'че ты хочешь?', ['Отмена', 'Одна песня', 'Весь плейлист']), bad_answer)
		return await method()

	server = get_server(ctx) # используется в подпрограммах (server.playlist)

	if len(args) == 0:
		await ctx.send(embed=MsgEmbed.error('Нифига ты быдло'))
		return

	# я не смог избавиться от флага
	if args[0] == '--id':
		if len(args) < 2: await ctx.send(embed=MsgEmbed.error('Недосдача по аргументам, жмот')); return
		if len(args) > 2: await ctx.send(embed=MsgEmbed.warning('Слишком много аргументов'))
		mi_list = VkSearch.byPlaylistId(args[1])
		is_playlist = True
	elif VkSearch.isCorrectPlaylistUrl(args[0]):
		if len(args) > 1: await ctx.send(embed=MsgEmbed.warning('Слишком много аргументов'))
		mi_list = VkSearch.byPlaylistUrl(args[0])
		is_playlist = True
	else:
		mi_list = VkSearch.byString(' '.join(args), 5)
		is_playlist = False
		return await add_one()
	
	if mi_list is None: await ctx.send(embed=MsgEmbed.error('Ошибка поиска!')); return
	if mi_list == []: await ctx.send(embed=MsgEmbed.warning('Ничего не найдено!')); return False
	
	if is_playlist: return await load_playlist()
	else: return await add_one()


@client.command(aliases=['r'])
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
		await ctx.send(embed=MsgEmbed.warning('Как может в казино быть колода разложена в другом порядке?! Ты чё, бредишь, что ли?! Ёбаный твой рот, а!..'))
		return
	
	mi = server.playlist.getByPosition(pos)
	playlist, voice = server.playlist, server.voice
	if pos == playlist.getPosition() and voice: voice.stop()
	if playlist.deleteByPosition(pos): await ctx.send(embed=MsgEmbed.info(f'Удалил: {mi.artist} - {mi.title} :fire:'))
	else: await ctx.send(embed=MsgEmbed.error('Ошибка удаления'))


@client.command(aliases=['pl'])
async def playing(ctx):
	playlist = get_server(ctx).playlist
	if playlist.getLength() == 0:
		await ctx.send(embed=MsgEmbed.warning('Плейлист пуст'))
		return
	await ctx.send(embed=get_mi_embed(playlist.getCurrent()))


@client.command(aliases=['q'])
async def queue(ctx):
	server = get_server(ctx)

	if server.playlist.getLength() == 0:
		await ctx.send(embed = MsgEmbed.info('Плейлист пуст'))
	else:
		mi_list = server.playlist.getAll()
		_list = [f'{i} :  {mi.artist} - {mi.title}' for i,mi in enumerate(mi_list)]
		pos = server.playlist.getPosition()
		_list[pos] = f'**{_list[pos]}**'

		emb = MsgEmbed.info('')
		emb.set_author(name = 'текущий плейлист', icon_url = icons['playlist'])
		await send_long_list(ctx, _list, emb, MsgEmbed.info(''))


@client.command(aliases=['ab'])
async def about(ctx):
	await ctx.send(embed=MsgEmbed.info(about_docs))
	pass	


@client.command(aliases=['m'])
async def mix(ctx):
	server = get_server(ctx)
	playlist = server.playlist
	if playlist.getLength() == 0:
		await ctx.send(embed=MsgEmbed.warning('Плейлист пуст, животное'))
		return
	playlist.mix()
	playlist.position = playlist.getLength() - 1
	await skip(ctx)

#endregion

import  discord
from discord.ext import commands

import os
import asyncio

import logging
logger = logging.getLogger(__name__)

from PlaylistAssistant import *
from Server import Server

pl_img     = 'https://img.icons8.com/pastel-glyph/FFFFFF/playlist.png'
search_img = 'https://img.icons8.com/pastel-glyph/FFFFFF/search--v2.png'
list_img   = 'https://img.icons8.com/windows/96/FFFFFF/untested.png'

def generate_embed_from_mi(mi):
	emb = discord.Embed(colour=0x007D80)
	emb.set_author(name = f'{mi.artist} - {mi.title} [ {mi.time} сек ]', icon_url = mi.image_url)
	return emb
Server.generate_embed = generate_embed_from_mi

client = commands.Bot(command_prefix=os.getenv('PREFIX'), case_insensitive=True)
client.remove_command('help')

servers = dict() # id : Server.Server


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

"""
@client.event
async def on_error(event, *args, **kwargs):
	message = args[0]
	logger.exception('on_error')
	await client.send_message(message.channel, ":anger: ОШИБКА!!!")

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send('Не дорос ещё!')
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send(f'Глаза разуй! Такой команды нет! `{ctx.prefix}help` - для справки')
	elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
		await ctx.send(f'Глаза разуй! Такого аргумента нет! `{ctx.prefix}help {ctx.command}` - для справки')
	else:
		logger.exception(error)
"""


@client.command()
async def help(ctx, cmd=''):
	if cmd == '':
		await ctx.send(help_docs['main-page'])
	elif cmd == 'not-exist':
		await ctx.send(help_docs['commands']['not-exist'].format(cmd=cmd))
	elif cmd in help_docs['commands']:
		await ctx.send(help_docs['commands'][cmd])
	else:
		await ctx.send(help_docs['commands']['not-exist'].format(cmd=cmd))


@client.command(pass_context = True)
async def join(ctx, channel_name = '', **kwargs):
	from_user = kwargs.get('from_user', True)
	server_id = ctx.message.guild.id
	if from_user: logger.debug(f'Server: {server_id}. Joining...')
	else: logger.debug(f'Server: {server_id}. Auto joining...')

	if channel_name == '':
		try:
			channel = ctx.author.voice.channel
		except AttributeError:
			logger.debug(f'Server: {server_id}. Join error: User is not connected')
			await ctx.send('Присоединись к каналу, мудак')
			return False
	else:
		channels = list(filter(lambda x: x.name==channel_name, ctx.guild.voice_channels))
		if len(channels) == 0:
			logger.debug(f'Server: {server_id}. Join error: Channel not found')
			await ctx.send('Ты инвалид, а название канала неправильное')
			return False
		elif len(channels) > 1:
			# даём пользователю выбрать канал по номеру в списке каналов
			emb_desc = '0. Отмена'
			for i, channel in enumerate(channels):
				emb_desc += f'\n{i+1} : {channel} ({channel.position+1}-й)'
			emb = discord.Embed(description=emb_desc, color=0x007D80)
			emb.set_author(name = 'выберите канал', icon_url = list_img)
			await ctx.send(embed = emb)

			def get_message_check(author):
				def is_message_correct(message):
					if message.author != author:
						return False
					return message.content.isdigit()
				return is_message_correct

			try:
				msg = await client.wait_for('message', check=get_message_check(ctx.author), timeout=10)
				index = int(msg.content)

				if index == 0:
					logger.debug(f'Server: {server_id}. Joining canceled')
					await ctx.send(embed = discord.Embed(description=f':warning: Подключение отменено', colour=0x007D80))
					return False
				if index > len(channels):
					await ctx.send(embed = discord.Embed(description=f':no_entry: Пользователь дурак. Подключение отменено', colour=0x007D80))
					return False
				channel = channels[index - 1]
			except asyncio.exceptions.TimeoutError:
				logger.debug(f'Server: {server_id}. Join error: User answer timeout')
				await ctx.send(embed = discord.Embed(description=f':warning: Подключение отменено', colour=0x007D80))
				return False
		else:
			channel = channels[0]

	if server_id in servers:
		server = servers[server_id]
	else:
		server = Server()
		server.ctx = ctx
		server.playlist = Playlist()
		servers[server_id] = server

	if server.voice is None:
		server.voice = await channel.connect()
		logger.debug(f'Server: {server_id}. Joined \'{channel}:{channel.position}\'')
		if from_user:
			await ctx.send(embed = discord.Embed(description=f':white_check_mark: Бот подключился к каналу: {channel}', colour=0x007D80))
	elif server.voice.is_connected():
		if server.voice.channel == channel:
			logger.debug(f'Server: {server_id}. Join error: Already joined')
			if from_user:
				await ctx.send(embed = discord.Embed(description=f':warning: Бот уже подключен к каналу: {channel}', colour=0x007D80))
			return True
		await server.voice.move_to(channel)
		logger.debug(f'Server: {server_id}. Joined \'{channel}:{channel.position}\'')
		await ctx.send(embed = discord.Embed(description=f':white_check_mark: Бот подключился к каналу: {channel}', colour=0x007D80))
	else:
		await server.voice.move_to(channel)
		logger.debug(f'Server: {server_id}. Joined \'{channel}:{channel.position}\'')
		if from_user:
			await ctx.send(embed = discord.Embed(description=f':white_check_mark: Бот подключился к каналу: {channel}', colour=0x007D80))

	return True


@client.command()
async def leave(ctx):
	server_id = ctx.message.guild.id
	if server_id in servers:
		await servers[server_id].voice.disconnect()
		await ctx.send(embed = discord.Embed(description=':no_entry: Бот отключился', colour=0x007D80))


@client.command()
async def play(ctx, *args):
	server_id = ctx.message.guild.id
	logger.debug(f'Server: {server_id}. Command \'play\'')
	if not await join(ctx, from_user=False): return
	server = servers[server_id]
	server.voice.resume()

	search_query = ' '.join(args)
	if search_query == '': return

	mi_list = musicSearch('vk', search_query, 5)
	if mi_list is None: await ctx.send('Ошибка поиска!'); return
	if mi_list == []: await ctx.send('Ничего не найдено!'); return

	# генерируем и отправляем список треков
	emb_desc = '0. Отмена'
	for i, mi in enumerate(mi_list):
		emb_desc += f'\n{i + 1} :  {mi.artist} - {mi.title}'
	emb = discord.Embed(description=emb_desc, color=0x007D80)
	emb.set_author(name = 'выберите песню', icon_url = search_img)
	await ctx.send(embed = emb)

	# ждём от пользователя индекс трека
	try:
		def get_message_check(author):
			def is_message_correct(message):
				if message.author != author:
					return False
				return message.content.isdigit()
			return is_message_correct

		while True:
			logger.debug(f'Server: {server_id}. Wait message from author: {ctx.author}')
			msg = await client.wait_for('message', check=get_message_check(ctx.author), timeout=10)
			text = msg.content

			try:
				index = int(text)
				if index == 0:
					logger.debug(f'Server: {server_id}. Canceled')
					await ctx.send('Отменено')
					return
				mi = mi_list[index - 1]
				logger.debug(f'Server: {server_id}. Received message from author: {ctx.author}')
				break
			except IndexError: await ctx.send('Ты кто такой, сука, чтоб это делать?')
	except asyncio.exceptions.TimeoutError:
		await ctx.send('Кто не успел - тот опоздал')
		return

	# пытаемся добавить трек в плейлист
	if server.playlist.add(mi): await ctx.send(f'Добавил: {mi.artist} - {mi.title}')
	else: await ctx.send('Ошибка добавления!'); return

	server.start()


@client.command()
async def pause(ctx):
	server_id = ctx.message.guild.id
	logger.debug(f'Server: {server_id}. Command \'pause\'')
	if server_id in servers:
		servers[server_id].voice.pause()


@client.command()
async def skip(ctx):
	server_id = ctx.message.guild.id
	logger.debug(f'Server: {server_id}. Command \'skip\'')
	if server_id in servers:
		servers[server_id].voice.stop()


@client.command()
async def playing(ctx):
	server_id = ctx.message.guild.id
	if not server_id in servers: return
	server = servers[server_id]
	if server.playlist.getLength() > 0:
		mi = server.playlist.getCurrent()
		await ctx.send(embed = generate_embed_from_mi(mi))


@client.command()
async def remove(ctx, pos: int):
	server_id = ctx.message.guild.id
	logger.debug(f'Server: {server_id}. Command \'remove\'')
	if not server_id in servers:
		logger.debug(f'Server: {server_id}. No server')
		await ctx.send('Туз не на месте')
		return
	server = servers[server_id]
	if server.playlist.getLength() == 0:
		logger.debug(f'Server: {server_id}. Empty playlist')
		await ctx.send('Ты говоришь, что в казино в запечатанных колодах карты разложены по-другому?!')
		return

	mi = server.playlist.getByPosition(pos)
	if mi is None:
		await ctx.send('Как может в казино быть колода разложена в другом порядке?! Ты чё, бредишь, что ли?! Ёбаный твой рот, а!..')
		return

	old_pos = server.playlist.getPosition()
	if server.playlist.deleteByPosition(pos):
		await ctx.send(f'Удалил: {mi.artist} - {mi.title} :fire:')
		if old_pos == pos: server.voice.stop()
	else:
		await ctx.send('Ошибка удаления')


@client.command()
async def queue(ctx):
	server_id = ctx.message.guild.id
	if not server_id in servers: await ctx.send('Плейлист не создан'); return
	server = servers[server_id]

	if server.playlist.getLength() == 0: await ctx.send('Плейлист пуст'); return

	mi_list = server.playlist.getAll()
	to_send = str()
	curr_id = server.playlist.getPosition()
	for i, mi in enumerate(mi_list):
		if i == curr_id:
			to_send += f'**{i} :  {mi.artist} - {mi.title}**\n'
		else:
			to_send += f'{i} :  {mi.artist} - {mi.title}\n'

	emb = discord.Embed(title='', description=to_send, color=0x007D80)
	emb.set_author(name = 'текущий плейлист', icon_url = pl_img)
	await ctx.send(embed = emb)

import  discord
from discord.ext import commands
from discord.utils import get

import os
import asyncio

import logging
logger = logging.getLogger(__name__)

from PlaylistAssistant import *
from Channel import Channel

pl_img = 'https://img.icons8.com/pastel-glyph/FFFFFF/playlist.png'
search_img = 'https://img.icons8.com/pastel-glyph/FFFFFF/search--v2.png'

def get_mi_embed(mi):
	emb = discord.Embed(colour = 0x007D80)
	emb.set_author(name = f'{mi.artist} - {mi.title} [ {mi.time} сек ]', icon_url = mi.image_url)
	return emb

client = commands.Bot(command_prefix=os.getenv('PREFIX'), case_insensitive=True)
client.remove_command('help')

channels = dict() # id : Channel.Channel

@client.event
async def on_ready():
	await client.change_presence(
		status=discord.Status.online,
		activity=discord.Activity(
			type=discord.ActivityType.watching,
			name="аниме"
		)
	)
	logger.info('Bot ready')

@client.event
async def on_error(event, *args, **kwargs):
	message = args[0]
	traceback = kwargs['traceback']
	logger.error(traceback.format_exc())
	await client.send_message(message.channel, ":anger: ОШИБКА!!!")


"""
@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send('Не дорос ещё!')
	if isinstance(error, commands.CommandNotFound):
		await ctx.send('Глаза разуй!')
"""


@client.command(pass_context = True)
async def join(ctx, **kwargs):
	from_user = kwargs.get('from_user', True)
	channel_id = ctx.message.guild.id
	logger.debug(f'Channel: {channel_id}. Command \'join\'')
	
	try:
		channel = ctx.author.voice.channel
	except AttributeError:
		await ctx.send('Присоединись к каналу, мудак')
		return False
	
	voice = get(client.voice_clients, guild=ctx.guild)
	if not (voice and voice.is_connected()):
		voice = await channel.connect()
		await ctx.send(embed = discord.Embed(description=f':white_check_mark: Бот подключился к каналу: {channel}', colour = 0x007D80))
	elif from_user:
		await ctx.send(embed = discord.Embed(description=f':warning: Бот уже подключен к каналу: {channel}', colour=0x007D80))

	if not channel_id in channels:
		channel = Channel()
		channel.ctx = ctx
		channel.voice = voice
		channel.playlist = Playlist()
		channels[channel_id] = channel
	else:
		# я не знаю нужно это вообще или нет, но на всякий случай впихнул
		channels[channel_id].voice = voice

	return True


@client.command()
async def leave(ctx):
	channel_id = ctx.message.guild.id
	if channel_id in channels:
		await channels[channel_id].voice.disconnect()
		await ctx.send(embed = discord.Embed(description=':no_entry: Бот отключился', colour = 0x007D80))


@client.command()
async def play(ctx, *args):
	channel_id = ctx.message.guild.id
	logger.debug(f'Channel: {channel_id}. Command \'play\'')
	if not await join(ctx, from_user=False): return
	channel = channels[channel_id]
	channel.voice.resume()

	search_query = ' '.join(args)
	if search_query == '': return

	mi_list = musicSearch('vk', search_query, 5)
	if mi_list is None: await ctx.send('Ошибка поиска!'); return
	if mi_list == []: await ctx.send('Ничего не найдено!'); return

	# генерируем и отправляем список треков
	emb_desc = '0. Отмена'
	for i, mi in enumerate(mi_list):
		emb_desc += f'\n{i + 1} :  {mi.artist} - {mi.title}'
	emb = discord.Embed(title='', description=emb_desc, color=0x007D80)
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
			logger.debug(f'Channel: {channel_id}. Wait message from author: {ctx.author}')
			msg = await client.wait_for('message', check=get_message_check(ctx.author), timeout=10)
			text = msg.content

			try:
				index = int(text)
				if index == 0:
					logger.debug(f'Channel: {channel_id}. Canceled')
					await ctx.send('Отменено')
					return
				mi = mi_list[index - 1]
				logger.debug(f'Channel: {channel_id}. Received message from author: {ctx.author}')
				break
			except IndexError: await ctx.send('Ты дурак? Тебе же показали какие цифры писать')
	except asyncio.exceptions.TimeoutError:
		await ctx.send('Кто не успел - тот опоздал')
		return

	# пытаемся добавить трек в плейлист
	if channel.playlist.add(mi): await ctx.send(f'Добавил: {mi.artist} - {mi.title}')
	else: await ctx.send('Ошибка добавления!'); return

	channel.start()


@client.command()
async def skip(ctx):
	channel_id = ctx.message.guild.id
	logger.debug(f'Channel: {channel_id}. Command \'skip\'')
	if channel_id in channels:
		channels[channel_id].voice.stop()


@client.command()
async def playing(ctx):
	channel_id = ctx.message.guild.id
	if not channel_id in channels: return
	channel = channels[channel_id]
	if channel.playlist.getLength() > 0:
		mi = channel.playlist.getCurrent()
		await ctx.send(embed = get_mi_embed(mi))
		

@client.command()
async def pause(ctx):
	channel_id = ctx.message.guild.id
	logger.debug(f'Channel: {channel_id}. Command \'pause\'')
	if channel_id in channels:
		channels[channel_id].voice.pause()


@client.command()
async def remove(ctx, pos: int):
	channel_id = ctx.message.guild.id
	logger.debug(f'Channel: {channel_id}. Command \'remove\'')
	if not channel_id in channels:
		logger.debug(f'Channel: {channel_id}. No channel')
		return
	channel = channels[channel_id]
	if channel.playlist.getLength() == 0:
		logger.debug(f'Channel: {channel_id}. Empty playlist')
		return
	
	mi = channel.playlist.getByPosition(pos)
	if mi is None:
		await ctx.send('Как может в казино быть колода разложена в другом порядке?! Ты чё, бредишь, что ли?! Ёбаный твой рот, а!..')
		return

	old_pos = channel.playlist.getPosition()
	if channel.playlist.deleteByPosition(pos):
		await ctx.send(f'Удалил: {mi.artist} - {mi.title} :fire:')
		if old_pos == pos: channel.voice.stop()
	else:
		await ctx.send('Ошибка удаления')
	
"""
@remove.error
async def remove_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send('Введи номер песни в плейлисте, которую хочешь убрать, если плейлист/песня под таким номером существует. Нумерация с нуля!')
	elif isinstance(error, commands.BadArgument):
		await ctx.send('Ты кто такой, сука, чтоб это делать?')
"""

@client.command()
async def queue(ctx):
	channel_id = ctx.message.guild.id
	if not channel_id in channels: await ctx.send('Плейлист не создан'); return
	channel = channels[channel_id]

	if channel.playlist.getLength() == 0: await ctx.send('Плейлист пуст'); return

	mi_list = channel.playlist.getAll()
	to_send = str()
	curr_id = channel.playlist.getPosition()
	for i, mi in enumerate(mi_list):
		if i == curr_id:
			to_send += f' -> {curr_id} :  {mi.artist} - {mi.title}\n'
		else:
			to_send += f'{i} :  {mi.artist} - {mi.title}\n'

	emb = discord.Embed(title='', description=to_send, color=0x007D80)
	emb.set_author(name = 'текущий плейлист', icon_url = pl_img)
	await ctx.send(embed = emb)


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
	
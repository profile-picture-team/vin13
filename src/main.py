import logging
import logging.config

#region shit
logging.basicConfig(filename="log/main.log", format='%(message)s', level=logging.DEBUG)
logging.debug('')
logging.root.removeHandler(logging.root.handlers[0])
logging.basicConfig(filename="log/debug.log", format='%(message)s', level=logging.DEBUG)
logging.debug('')
#endregion

logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger(__name__)
# надо разобраться с этими логерами (ну так разберись)
# лол, а я знаю как?
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

import sys, os, atexit, asyncio, platform
loop = asyncio.get_event_loop()

import Bot
import HelpLoader
import AboutLoader

def main():
	
	def on_exit():
		logger.info('Shutdown bot')
		loop.run_until_complete(Bot.client.logout())
		
		logger.info('Stop playing threads...')
		servers = Bot.servers.values()
		for server in servers: server.stop()
		for server in servers: server.playing_thread.join()

		for task in asyncio.Task.all_tasks():
			logger.info(f'Cancel {task.get_coro()}')
			task.cancel()
		loop.stop()

		logger.info('Program end.')
		sys.exit(0)

	def on_terminate(sighnum, frame):
		logger.warning('Non ^C closing!')
		sys.exit(0)

	atexit.register(on_exit)
	if platform.system() != 'Windows': # я знаю, что можно использвать sys, но нихачу
		import signal
		signal.signal(signal.SIGHUP, on_terminate)
		logger.warning('It is recommended to stop the program in ^C')
	else: 
		logger.warning('Stop program in ^C')

	try:
		logger.info('Program start')
		prefix = os.getenv('PREFIX')
		Bot.help_docs = HelpLoader.load_help_docs('conf/help.json', prefix)
		Bot.about_docs = AboutLoader.load_about_docs('conf/about.json', prefix)
		logger.info('Bot starts and preparing to work')
		loop.run_until_complete(Bot.client.start(os.getenv('BOT_TOKEN')))
	except KeyboardInterrupt:
		logger.warning('Interrupted')
		sys.exit(0)
	except Exception as error:
		logger.exception(error)

if __name__ == '__main__': main()

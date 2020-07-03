import logging
import logging.config

logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

import sys, os, platform

import Bot
import HelpLoader
import AboutLoader

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

def stop_playing_threads(servers):
	logger.info('Stop playing threads...')
	for server in servers: server.stop()
	for server in servers: server.playing_thread.join()

@run_once
def exit():
	try:
		logger.info('Shutdown bot')
		stop_playing_threads(Bot.servers.values())
	except Exception as err:
		logger.exception(f'Error while exiting: {err}')
		logger.error('Program ended with error!\n')
		sys.exit(1)
	else:
		logger.info('Program end.\n')
		sys.exit(0)

def main():
	if platform.system() != 'Windows': # я знаю, что можно использовать sys, но нихачу
		def on_terminate(sighnum, frame): exit()
		import signal; signal.signal(signal.SIGHUP, on_terminate)
		print('Achtung: It is recommended to stop program in ^C')
	else: print('Achtung: Stop program in ^C')

	try:
		logger.info('Program start')
		prefix = os.getenv('PREFIX')
		Bot.help_docs = HelpLoader.load_help_docs('conf/help.json', prefix)
		Bot.about_docs = AboutLoader.load_about_docs('conf/about.json', prefix)
		logger.info('Bot starts and preparing to work')
		Bot.client.run(os.getenv('BOT_TOKEN'))
	except KeyboardInterrupt: logger.warning('Interrupted'); exit()
	except Exception as error: logger.exception(error)
	finally: exit()

if __name__ == '__main__': main()

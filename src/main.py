import logging
import logging.config

#region shit
logging.basicConfig(filename="log/main.log", format='%(message)s', level=logging.DEBUG)
logging.debug('####################\n')
logging.root.removeHandler(logging.root.handlers[0])
logging.basicConfig(filename="log/debug.log", format='%(message)s', level=logging.DEBUG)
logging.debug('####################\n')
#endregion

logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger(__name__)
# надо разобраться с этими логерами (ну так разберись)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

import sys, os, signal

import Bot
import HelpLoader
import AboutLoader

def main():
	def exit(sighnum = None, frame = None):
		logger.info('Stop playing threads...')
		servers = Bot.servers.values()
		for server in servers: server.stop()
		for server in servers: server.playing_thread.join()
		logger.info('Program end.\n')
		sys.exit(0)
	signal.signal(signal.SIGHUP, exit)
	try:
		logger.info('Program start')
		prefix = os.getenv('PREFIX')
		Bot.help_docs = HelpLoader.load_help_docs('conf/help.json', prefix)
		Bot.about_docs = AboutLoader.load_about_docs('conf/about.json', prefix)
		Bot.client.run(os.getenv('BOT_TOKEN'))
	except KeyboardInterrupt:
		logger.warning('Interrupted')
	except Exception as error:
		logger.exception(error)
	finally:
		exit()

if __name__ == '__main__': main()

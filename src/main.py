import logging
import logging.config
logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger(__name__)
# надо разобраться с этими логерами (ну так разберись)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

import os

import Bot
import HelpLoader
import AboutLoader

def main():
	try:
		logger.info('####################') #ыыы
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
		logger.info('Stop playing threads...')
		servers = Bot.servers.values()
		for server in servers: server.stop()
		for server in servers: server.playing_thread.join()
		logger.info('Program end.')

if __name__ == '__main__': main()

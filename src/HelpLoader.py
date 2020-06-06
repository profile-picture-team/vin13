import json


def generate_main_page(main_content, prefix, left_margin=3, color_scheme=''):
	""" Генерирует главную страницу справки """
	header = ('\n'.join(main_content['header']) + '\n').format(prx=prefix)
	footer = ('\n'.join(main_content['footer']) + '\n').format(prx=prefix)

	commands = main_content['commands']
	maxl = len(max(commands.keys(), key=lambda x: len(x)))
	patern = ' '*left_margin + '{prx}{cmd:'+str(maxl)+'} - {des}\n'

	main = str()
	for command in commands.keys():
		main += patern.format(
			cmd=command,
			des=commands[command].format(prx=prefix),
			prx=prefix
		)

	return f"```{color_scheme}\n" + header + main + footer + '```'


def generate_cmd_page(cmd_name, cmd_content, prefix, left_margin=3, color_scheme=''):
	""" Генерирует страницу справки по команде """

	header = 'Справка: {}{}\n'.format(prefix, cmd_name)
	if cmd_content is None:
		return f"```{color_scheme}\n" + header + '\nСтраница отсутствует\n```'

	description = ('\n'.join(cmd_content['description']) +'\n').format(prx=prefix)

	if len(cmd_content.get('templates', [])) > 0:
		templates = '\nШаблоны:\n'
		for template in cmd_content['templates']:
			templates += ' '*left_margin + prefix + template + '\n'
	else: templates = ''

	if len(cmd_content.get('examples', [])) > 0:
		examples = '\nПримеры:\n'
		for example in cmd_content['examples']:
			examples += ' '*left_margin + prefix + example + '\n'
	else: examples = ''

	return f"```{color_scheme}\n"+header+description+templates+examples+'```'


def load_help_docs(filepath, prefix):
	""" Загружает справку из файла """
	help_content = json.load(open(filepath, 'r', encoding='utf-8'))

	lmargin = help_content['left-margin']
	colors = help_content['color-scheme']

	help_docs = dict()
	help_docs['main-page'] = generate_main_page(help_content['main'], prefix, lmargin, colors)
	help_docs['commands'] = dict()
	help_docs['commands']['not-exist'] = generate_cmd_page('{cmd}', None, prefix, lmargin, colors)

	for cmd, content in help_content['commands'].items():
		help_docs['commands'][cmd] = generate_cmd_page(cmd, content, prefix, lmargin, colors)

	return help_docs

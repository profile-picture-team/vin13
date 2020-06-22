import json


def load_about_docs(filepath, prefix):
	about = json.load(open(filepath, 'r', encoding='utf-8'))
	values = dict()
	values['botname'] = about['botname']
	values['prx'] = prefix
	
	text = '\n'.join(about['description']).format(**values)
	authors = 'Авторы: '
	authors += ', '.join(about['authors'][:-1])
	authors += ' и ' + about['authors'][-1]
	version = 'Версия: ' + about['version']
	github = 'GitHub: ' + about['github']

	return '\n'.join([
		text, '',
		authors,
		version,
		github
	])
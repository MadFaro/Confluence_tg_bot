import pandas as pd


def open_file(file, writer, mode):
	with open(file, mode = mode, encoding = 'utf-8') as output:
		output.write(writer)
		output.close()

def login_true(login, file_bd, file_ad):
	if (login not in list(set(pd.read_csv(file_bd, delimiter = '_', index_col=None)['id'].to_list())) and
		login not in list(set(pd.read_csv(file_ad, delimiter = '_', index_col=None)['id'].to_list()))):
		return True
	if (login not in list(set(pd.read_csv(file_bd, delimiter = '_', index_col=None)['id'].to_list())) and
		login in list(set(pd.read_csv(file_ad, delimiter = '_', index_col=None)['id'].to_list()))):
		return False

def log(id):
	try:
		login = str(pd.read_csv('\\Desktop\\bot\\Login\\Pass\\' + str(id) + 'log.txt').columns[0])
		return login
	except:
		return None

def Password(id):
	try:
		Password = str(pd.read_csv('\\Desktop\\bot\\Login\\Pass\\' + str(id) + 'Pass.txt').columns[0])
		return Password
	except:
		return None
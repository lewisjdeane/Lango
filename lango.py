import codecs
import configparser
import random

lines = []
mode  = "LTF"


def main():
	print_intro_message()
	load_file()
	load_mode()
	main_loop()
	

def main_loop():
	(x, y) = get_word()

	message = input("\n%s\n" % x)

	if message == "exit":
		exit()
	elif message.startswith("set path "):
		set_path(message.strip("set path "))
	elif message.startswith("set mode "):
		set_mode(message.strip("set mode "))
	elif message.lower() == y.lower():
		print("Correct!")
	else:
		print("Incorrect, correct answer was '%s'" % (y))

	main_loop()


def load_file():
	global lines

	config = configparser.ConfigParser()
	config.read('config.ini')

	try:
		path = config['GENERAL']['Path']
	except KeyError:
		path = input("INFO: No target filepath set, please enter a filepath: ")
		set_path(path)

	y = [line.rstrip('\n') for line in codecs.open(path, 'r', encoding='utf-8')]
	lines = [seperate(x) for x in y]


def set_path(path):
	config = configparser.ConfigParser()
	config.read('config.ini')
	
	try:
		general = config['GENERAL']
	except KeyError:
		config['GENERAL'] = {}
		general = config['GENERAL']
	
	general['Path'] = path

	with open('config.ini', 'w') as configfile:
		config.write(configfile)

	print("INFO: Set path to %s\n" % (path))


def set_mode(mode1):
	global mode

	mode = mode1

	config = configparser.ConfigParser()
	config.read('config.ini')

	try:
		general = config['GENERAL']
	except KeyError:
		config['GENERAL'] = {}
		general = config['GENERAL']

	general['Mode'] = mode1

	with open('config.ini', 'w') as configfile:
		config.write(configfile)

	print("INFO: Set mode to %s\n" % (mode1))


def seperate(x):
	y = x.split(" - ", 1)
	return (y[0], y[1].strip('\r'))


def load_mode():
	global mode

	config = configparser.ConfigParser()
	config.read('config.ini')

	try:
		mode = config['GENERAL']['Mode']
	except KeyError:
		mode = input("INFO: No mode set, please enter a valid mode (MIX, F2L or L2F): ")
		set_mode(mode)


def get_word():
	global lines
	global mode

	rand = random.randint(0, len(lines) - 1)
	
	if mode == "F2L":
		index = 0
	elif mode == "L2F":
		index = 1
	else:
		index = random.randint(0, 1)

	line = lines[rand]

	return (line[index], line[index ^ 1])


def print_intro_message():
	print("Welcome to lango! Run 'lango-help' to get show documentation on how to use lango.\n")


main()
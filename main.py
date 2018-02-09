#!/usr/bin/env python3
import sys
if sys.version_info < (3,6):
	print("Interpreter error. Use Python interpreter version 3.6 or greater")
	sys.exit(1)

#Импорт класса для работы с файловой системой
from file_system import FileSystem

#Импорт классов для синтаксического анализа
from parser.arg_parser import ArgParser
from parser.config_parser import ConfigParser
from parser.test_parser import TestParser

def main():
	#Парсинг аргументов командной строки
	config_file, tests_files = ArgParser().parse_arguments()

	#Парсинг конфигурационного файла
	config = ConfigParser(FileSystem).parse_config(config_file)

if __name__ == "__main__":
	main()
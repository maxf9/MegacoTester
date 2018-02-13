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

#Импорт класса очереди для синхронизации потоков выполнения программы
from queue import Queue

def main():
	#Парсинг аргументов командной строки
	config_file, tests_files = ArgParser().parse_arguments()

	#Парсинг конфигурационного файла
	config = ConfigParser(FileSystem).parse_config(config_file)

	#Создание очереди FIFO от парсера тестовых сценариев до процессора
	from_parser = Queue()
	#Создание очереди FIFO от процессора до логгера тестовых сценариев
	from_processor = Queue()

	#Создание и конфигурация парсера тестовых сценариев
	test_parser = TestParser(FileSystem, tests_files, queue_to_processor=from_parser)

if __name__ == "__main__":
	main()
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

#Импорт класса реализации процессора
from processor.core import Processor

#Импорт класса реализации логгера тестовых сценариев
from test_logger import TestLogger

#Импорт класса очереди для синхронизации потоков выполнения программы
from queue import Queue

def main():
	#Парсинг аргументов командной строки
	config_file, tests_files = ArgParser().parse_arguments()

	#Парсинг конфигурационного файла
	config = ConfigParser(FileSystem).parse_config(config_file)

	#Создание двух очередей синхронизации между потоками программы
	queues = [Queue() for i in range(2)]

	#Создание и конфигурация парсера тестовых сценариев
	test_parser = TestParser(FileSystem, tests_files, to_processor=queues[0])

	#Создание и конфигурация процессора
	processor = Processor(FileSystem, config, from_parser=queues[0], to_logger=queues[1])

	#Создание и конфигурация логгера тестовых сценариев
	test_logger = TestLogger(FileSystem, from_processor=queues[1])

if __name__ == "__main__":
	main()
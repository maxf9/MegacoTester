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
#Импорт класса кадра для обмена сообщениями между потоками
from frame import Frame

#Объявление классов FileSystem и Frame в пространстве имен __builtins__
setattr(__builtins__, 'FileSystem', FileSystem)
setattr(__builtins__, 'Frame', Frame)

def main():
	#Парсинг аргументов командной строки
	config_file, tests_files = ArgParser().parse_arguments()

	#Парсинг конфигурационного файла
	config = ConfigParser().parse_config(config_file)

	#Создание двух очередей синхронизации между потоками программы
	queues = [Queue() for i in range(2)]

	#Создание и конфигурация парсера тестовых сценариев
	test_parser = TestParser(tests_files, test_queue=queues[0], log_queue=queues[1])

	#Создание и конфигурация процессора
	processor = Processor(config, Frame, test_queue=queues[0], log_queue=queues[1])

	#Создание и конфигурация логгера тестовых сценариев
	test_logger = TestLogger(FileSystem, Frame, log_dir=config.log_dir, log_queue=queues[1])

	#Запуск компонентов приложения
	test_logger.start()
	processor.start()
	test_parser.start()

	#Ожидание завершения работы компонентов приложения
	test_parser.join()
	processor.join()
	test_logger.join()

if __name__ == "__main__":
	main()
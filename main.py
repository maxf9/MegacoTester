#!/usr/bin/env python3
import sys
if sys.version_info < (3,6):
	print("Interpreter error. Use Python interpreter version 3.6 or greater")
	sys.exit(1)

from parser.arg_parser import ArgParser
from parser.config_parser import ConfigParser
from parser.test_parser import TestParser

def main():
	#Парсинг аргументов командной строки
	config_file, tests_files = ArgParser().parse_arguments()

if __name__ == "__main__":
	main()
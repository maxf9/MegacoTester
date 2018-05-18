#!/usr/bin/env python3
import sys
if sys.version_info < (3,6):
	print("Interpreter Error: use Python interpreter version 3.6 or greater")
	sys.exit(1)

# Importing class for working with file system
from file_system import FileSystem

# Importing classes for parsing purposes
from parser.arg_parser import ArgParser
from parser.config_parser import ConfigParser
from parser.test_parser import TestParser

# Importing class for tests processing
from processor.core import Processor

# Importing class for tests results logging
from test_logger import TestLogger

# Importing classes for main instances interaction
from frame import Frame
from multiprocessing import Queue

# Importing functions and attributes for UNUX signal handling
from signal import signal, SIGINT

# Make FileSystem and Frame classes available in all modules
setattr(__builtins__, 'FileSystem', FileSystem)
setattr(__builtins__, 'Frame', Frame)

def main():

	def signal_handler(*args):
		for process in (test_parser, processor, test_logger):
			if process.is_alive():
				process.terminate()
				process.join()
		print("\nSTOP!")
		sys.exit(1)

	signal(SIGINT, signal_handler)

	# Parsing the command-line arguments
	config_file, tests_files = ArgParser().parse_arguments()

	# Parsing the configuration file
	config = ConfigParser().parse_config(config_file)

	# Creating two synchronization queues between program threads
	queues = [Queue() for i in range(2)]

	# Creating and configuring a parser for test scenarios
	test_parser = TestParser(tests_files, test_queue=queues[0], log_queue=queues[1])

	# Creating and configuring a logger for test scenarios
	test_logger = TestLogger(log_dir=config.log_dir, log_queue=queues[1])

	# Creating and configuring the processor
	processor = Processor(config, test_logger.result_directory_name, test_queue=queues[0], log_queue=queues[1])

	# Launching the main instances of application
	test_logger.start()
	processor.start()
	test_parser.start()

	# Stopping the main instances of application
	test_parser.join()
	processor.join()
	test_logger.join()

if __name__ == "__main__":
	with open("/dev/null") as sys.stderr:
		main()
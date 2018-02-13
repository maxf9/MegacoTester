from argparse import ArgumentParser

class ArgParser:

	_instance = None
	_arg_parser = ArgumentParser()

	def __new__(cls, *args, **kwargs):
		if ArgParser._instance is None:
			ArgParser._instance = object.__new__(cls)
		return ArgParser._instance

	def __init__(self):
		ArgParser._define_args()

	@classmethod
	def _define_args(cls):
		cls._arg_parser.add_argument("-c", "--config", action="store", type=str, dest="config", required=True)
		cls._arg_parser.add_argument("-t", "--tests", action="store", nargs="+", type=str, dest="tests", required=True)

	def parse_arguments(self):
		namespace = ArgParser._arg_parser.parse_args()
		return (namespace.config, namespace.tests)
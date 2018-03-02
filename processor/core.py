from threading import Thread
from queue import Queue
from processor.interpreter import Interpreter

class Processor(Thread):

	_instance = None
	_file_system = None
	_interpreter = None

	def __new__(cls, *args, **kwargs):
		if Processor._instance is None:
			Processor._instance = object.__new__(cls)
		return Processor._instance

	def __init__(self, file_system, config, from_parser, to_logger):
		super().__init__()
		self.parser_queue = from_parser
		self.logger_queue = to_logger
		self._interpreter_queue = Queue()
		Processor._file_system = file_system
		Processor._interpreter = Interpreter(config, self._interpreter_queue)

	def run(self):
		pass
	
from threading import Thread

class Processor(Thread):

	_instance = None
	_config = None
	_file_system = None

	def __new__(cls, *args, **kwargs):
		if Processor._instance is None:
			Processor._instance = object.__new__(cls)
		return Processor._instance

	def __init__(self, file_system, config, from_parser, to_logger):
		super().__init__()
		self.parser_queue = from_parser
		self.logger_queue = to_logger
		Processor._file_system = file_system
		Processor._config = config

	def run(self):
		pass
	
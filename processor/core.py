from threading import Thread

class Processor(Thread):

	_instance = None
	_config = None
	_file_system = None

	def __new__(cls, *args, **kwargs):
		if Processor._instance is None:
			Processor._instance = object.__new__(cls)
		return Processor._instance

	def __init__(self, file_system, config, queue):
		super().__init__()
		self.logger_queue = queue
		Processor._file_system = file_system
		Processor._config = config

	def run(self):
		pass
	
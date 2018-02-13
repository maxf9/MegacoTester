from threading import Thread

class TestLogger(Thread):

	_instance = None
	_file_system = None
	
	def __new__(cls, *args, **kwargs):
		if TestLogger._instance is None:
			TestLogger._instance = object.__new__(cls)
		return TestLogger._instance

	def __init__(self, file_system, from_processor):
		super().__init__()
		self.processor_queue = from_processor
		TestLogger._file_system = file_system

	def run(self):
		pass
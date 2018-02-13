from threading import Thread

class TestParser(Thread):

	_instance = None
	_file_system = None

	def __new__(cls, *args, **kwargs):
		if TestParser._instance is None:
			TestParser._instance = object.__new__(cls)
		return TestParser._instance
	
	def __init__(self, file_system, tests_files, queue_to_processor):
		super().__init__()
		self.tests_files =  tests_files
		self.queue_to_processor = queue_to_processor
		TestParser._file_system = file_system

	def run(self):
		pass
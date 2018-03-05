from threading import Thread
from queue import Empty

class TestLogger(Thread):

	_instance = None
	_file_system = None
	_frame = None
	
	def __new__(cls, *args, **kwargs):
		if TestLogger._instance is None:
			TestLogger._instance = object.__new__(cls)
		return TestLogger._instance

	def __init__(self, file_system, frame, log_queue):
		super().__init__()
		self.log_queue = log_queue
		TestLogger._file_system = file_system
		TestLogger._frame = frame

	def run(self):
		stop_counter = 0
		while True:
			try:
				frame = self.log_queue.get(block=True, timeout=0.1)
				if frame.header == TestLogger._frame.STOP:
					stop_counter += 1
					if stop_counter == 2: break
			except Empty:
				continue
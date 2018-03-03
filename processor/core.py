from threading import Thread
from queue import Queue, Empty
from processor.interpreter import Interpreter

class Processor(Thread):

	_instance = None
	_interpreter = None

	def __new__(cls, *args, **kwargs):
		if Processor._instance is None:
			Processor._instance = object.__new__(cls)
		return Processor._instance

	def __init__(self, config, from_parser, to_logger):
		super().__init__()
		self.parser_queue = from_parser
		self.logger_queue = to_logger
		self._interpreter_queue = Queue()
		Processor._interpreter = Interpreter(config, self._interpreter_queue)

	def run(self):
		#Запуск процесса интерпретатора
		Processor._interpreter.start()
		while True:
			try:
				frame = self.parser_queue.get(block=True, timeout=0.1)
				if frame.header == "stop":
					break
				else:
					self._interpreter_queue.put(frame)
			except Empty:
				continue
		Processor._interpreter.join()


	
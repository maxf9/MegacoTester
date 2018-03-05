from threading import Thread
from queue import Queue, Empty
from processor.interpreter import Interpreter

class Processor(Thread):

	_instance = None
	_frame = None
	_interpreter = None

	def __new__(cls, *args, **kwargs):
		if Processor._instance is None:
			Processor._instance = object.__new__(cls)
		return Processor._instance

	def __init__(self, config, frame, test_queue, log_queue):
		super().__init__()
		self.test_queue = test_queue
		self.log_queue = log_queue
		Processor._frame = frame
		Processor._interpreter = Interpreter(config)

	def execute_test(self, scenario):
		pass

	def run(self):
		#Запуск интерпретации тестовых сценариев
		while True:
			try:
				frame = self.test_queue.get(block=True, timeout=0.1)
				if frame.header == Processor._frame.STOP:
					break
				else:
					self.execute_test(frame.payload)
			except Empty:
				continue
		#Отправка стопового кадра по завершению интерпретации
		self.log_queue.put(Processor._frame(Processor._frame.STOP))


	
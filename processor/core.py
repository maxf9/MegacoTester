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

	def _execute_test(self, test):
		#Выполнение тестового сценария интерпретатором
		result,log = Processor._interpreter.execute(test.scenario)
		#Отправка отчета о выполнении теста
		self.log_queue.put(Processor._frame(Processor._frame.REPORT, 
				                            Processor._frame.Report(Processor._frame.Report.EXECUTE, result, log, test.name)))

	def run(self):
		#Запуск интерпретации тестовых сценариев
		while True:
			try:
				frame = self.test_queue.get(block=True, timeout=0.1)
				if frame.header == Processor._frame.STOP:
					break
				else:
					self._execute_test(frame.payload)
			except Empty:
				continue
		#Остановка работы всех сетевых адаптеров
		Processor._interpreter.stop_all_network_adapters()
		#Отправка стопового кадра по завершению интерпретации
		self.log_queue.put(Processor._frame(Processor._frame.STOP))


	
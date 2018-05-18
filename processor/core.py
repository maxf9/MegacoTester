from processor.interpreter import ScenarioInterpreter
from processor.scenario_builder import ScenarioBuilder
from multiprocessing import Process
from queue import Empty
import lxml.etree as xml

class Processor(Process):

	_instance = None
	_builder = None
	_interpreter = None

	def __new__(cls, *args, **kwargs):
		if Processor._instance is None:
			Processor._instance = object.__new__(cls)
		return Processor._instance

	def terminate(self):
		Processor._interpreter.stop_all_network_adapters()
		super().terminate()

	def __init__(self, config, result_directory, test_queue, log_queue):
		super().__init__()
		self.test_queue = test_queue
		self.log_queue = log_queue
		Processor._builder = ScenarioBuilder()
		Processor._interpreter = ScenarioInterpreter(config)

	def _execute_test(self, test):
		scenario = Processor._builder.build_scenario(xml.fromstring(test.instructions))
		#Выполнение тестового сценария интерпретатором
		result, log = Processor._interpreter.execute(scenario)
		#Отправка отчета о выполнении теста
		self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.EXECUTE, result, log, test.name)))

	def run(self):
		#Запуск интерпретации тестовых сценариев
		while True:
			try:
				frame = self.test_queue.get(block=True, timeout=0.1)
				if frame.header == Frame.STOP:
					break
				else:
					self._execute_test(frame.payload)
			except Empty:
				continue
		#Остановка работы всех сетевых адаптеров
		Processor._interpreter.stop_all_network_adapters()
		#Отправка стопового кадра по завершению интерпретации
		self.log_queue.put(Frame(Frame.STOP))


	
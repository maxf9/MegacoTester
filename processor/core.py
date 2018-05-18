from processor.interpreter import ScenarioInterpreter
from processor.scenario_builder import ScenarioBuilder
from threading import Thread, Event
from multiprocessing import Process
from scapy.all import sniff
from queue import Empty
import lxml.etree as xml
from time import sleep

class Processor(Process):

	_instance = None
	_builder = None
	_sniffer = None
	_interpreter = None

	def __new__(cls, *args, **kwargs):
		if Processor._instance is None:
			Processor._instance = object.__new__(cls)
		return Processor._instance

	def terminate(self):
		Processor._sniffer.stop(no_wait=True)
		Processor._interpreter.stop_all_network_adapters()
		super().terminate()

	def __init__(self, config, test_queue, log_queue):
		super().__init__()
		self.test_queue = test_queue
		self.log_queue = log_queue
		Processor._builder = ScenarioBuilder()
		Processor._sniffer = Sniffer()
		Processor._interpreter = ScenarioInterpreter(config)

	def _execute_test(self, test):
		# Создание сценария
		scenario = Processor._builder.build_scenario(xml.fromstring(test.instructions))
		# Запуск сниффера для теста
		Processor._sniffer.start(test.name)
		#Выполнение тестового сценария интерпретатором
		result, log = Processor._interpreter.execute(scenario)
		# Остановка сниффера для теста
		Processor._sniffer.stop()
		#Получение пакетов из буффера
		dump = Processor._sniffer.get_buffer()
		#Отправка отчета о выполнении теста
		self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.EXECUTE, result, log, dump, test.name)))

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

class Sniffer:
	
	def __init__(self):
		self._sniff_thread = None
		self._packet_buffer = None
		self._pcap_filename = None
		self._event = Event()

	def _dump_packet(self, packet):
		self._packet_buffer.append(packet)

	def _reset_all(self):
		self._sniff_thread = None
		self._packet_buffer = []
		self._event.clear()

	def start(self, pcap_filename):
		self._reset_all()
		self._pcap_filename = pcap_filename
		self._sniff_thread = Thread(target=sniff, kwargs={"prn" : self._dump_packet, "stop_filter" : lambda p: self._event.isSet(), "store" : 0})
		self._sniff_thread.start()
		sleep(1)

	def get_buffer(self):
		return self._packet_buffer

	def stop(self, no_wait=False):
		if not no_wait:
			sleep(1)
		self._event.set()
		self._sniff_thread.join()
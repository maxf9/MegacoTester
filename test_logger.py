from threading import Thread
from queue import Empty

class TestLogger(Thread):

	_instance = None
	
	def __new__(cls, *args, **kwargs):
		if TestLogger._instance is None:
			TestLogger._instance = object.__new__(cls)
		return TestLogger._instance

	def __init__(self, file_system, frame, log_dir, log_queue):
		super().__init__()
		self.log_dir = log_dir
		self.log_queue = log_queue
		self._parse_log = {"success" : [], "failure" : []}

	def _form_parse_log_output(self):
		output = "SUCCESSFULLY PARSED:\n"
		for log in self._parse_log["success"]: output += log
		output += "\nUNSUCCESSFULLY PAPSED:\n"
		for log in self._parse_log["failure"]: output += log 
		return output

	def _handle_report(self, report):
		if report.action == Frame.Report.PARSE:
			if report.success:
				self._parse_log["success"] += [report.log + "\n"]
			else:
				self._parse_log["failure"] += [report.log + "\n"]
		elif report.action == Frame.Report.EXECUTE:
			test_log = ("EXECUTE STATUS: SUCCESS\n\n" if report.success else "EXECUTE STATUS: FAILURE\n\n") + report.log
			FileSystem.dump_to(self.log_dir + "/" + "results" + "/" + report.test_name + ".log", test_log)

	def run(self):
		stop_counter = 0
		#Создание директории для записи логов тетовых сценариев
		FileSystem.create_dir(self.log_dir + "/" + "results")
		while True:
			try:
				frame = self.log_queue.get(block=True, timeout=0.1)
				if frame.header == Frame.STOP:
					stop_counter += 1
					if stop_counter == 2: break
				else:
					self._handle_report(frame.payload)
			except Empty:
				continue
		#Выгрузка логов парсинга
		FileSystem.dump_to(self.log_dir + "/" + "test_parser.log", self._form_parse_log_output())
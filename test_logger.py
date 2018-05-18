from asyncio import new_event_loop, as_completed
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, cpu_count
from queue import Empty
from time import strftime


class TestLogger(Process):

	_instance = None
	
	def __new__(cls, *args, **kwargs):
		if TestLogger._instance is None:
			TestLogger._instance = object.__new__(cls)
		return TestLogger._instance

	def __init__(self, log_dir, log_queue):
		super().__init__()
		self.log_queue = log_queue
		self.result_directory_name = log_dir + "/" + "MegacoTester_Results_" + strftime("%d.%m.%Y_%Hh-%Mm-%Ss")
		self._event_loop = new_event_loop()
		self._thread_executor = ThreadPoolExecutor(max_workers=cpu_count())
		self._stop_counter = 0
		self._parse_logs = {"success" : [], "failure" : []}
		self._create_result_directory()

	def _create_result_directory(self):
		FileSystem.create_dir(self.result_directory_name)
		FileSystem.create_dir(self.result_directory_name + "/" + "Log")
		FileSystem.create_dir(self.result_directory_name + "/" + "Dump")

	def _form_test_parser_log(self):
		test_parser_log = "SUCCESSFULLY PARSED:\n"
		for parse_log in self._parse_logs["success"]:
			test_parser_log += parse_log
		test_parser_log += "\nUNSUCCESSFULLY PAPSED:\n"
		for parse_log in self._parse_logs["failure"]:
			test_parser_log += parse_log
		return test_parser_log

	def _dump_test_parser_log(self):
		FileSystem.dump_to(self.result_directory_name + "/" + "Test_Parser.log", self._form_test_parser_log())

	async def _record_logs(self, report):
		if report.action == Frame.Report.PARSE:
			if report.success:
				self._parse_logs["success"] += [report.log]
			else:
				self._parse_logs["failure"] += [report.log]
		elif report.action == Frame.Report.EXECUTE:
			test_log = ("EXECUTE STATUS: SUCCESS\n\n" if report.success else "EXECUTE STATUS: FAILURE\n\n") + report.log
			for task in as_completed([self._event_loop.run_in_executor(self._thread_executor, FileSystem.dump_to, 
				                                                       self.result_directory_name + "/Log/" + report.test_name + ".log", test_log)]):
				await task

	async def _handle_reports(self):
		while True:
			try:
				for task in as_completed([self._event_loop.run_in_executor(self._thread_executor, self.log_queue.get, True, 0.1)]):
					frame = await task
					if frame.header == Frame.STOP:
						self._stop_counter += 1
					else:
						await self._record_logs(frame.payload)
			except Empty:
				if self._stop_counter == 2:
					break

	def run(self):
		self._event_loop.run_until_complete(self._handle_reports())
		self._event_loop.close()
		self._dump_test_parser_log()
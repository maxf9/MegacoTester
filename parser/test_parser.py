from parser.scenario_builder import ScenarioBuilder
from concurrent.futures import ThreadPoolExecutor
from asyncio import get_event_loop, as_completed
from multiprocessing import cpu_count
from threading import Thread
from os.path import dirname
import lxml.etree as xml
from sys import exit


class TestParser(Thread):
	"""Class for parsing test files"""

	_instance = None

	def __new__(cls, *args, **kwargs):
		if TestParser._instance is None:
			TestParser._instance = object.__new__(cls)
		return TestParser._instance
	
	def __init__(self, tests_files, test_queue, log_queue):
		super().__init__()
		self.tests_files = tests_files              # List of paths to tests files
		self.test_queue = test_queue                # FIFO queue to the Processor instance 
		self.log_queue = log_queue                  # FIFO queue to the TestLogger instance
		self._validator = ScenarioValidator()       # Validator for the tests files
		self._scenario_builder = ScenarioBuilder()  # Builder for the Scenario instance
		self._event_loop = get_event_loop()         # Getting an event loop for asynchronous task processing
		self._thread_executor = ThreadPoolExecutor(max_workers=cpu_count())  # Thread pool for blocking tasks (number of workers = number of CPUs)

	async def validate_test(self, content):
		"""Asynchronous wrapper for the _validator.validate_scenario method"""
		return self._validator.validate_scenario(content)

	@staticmethod
	async def decode_xml(content):
		"""Asynchronous wrapper for the XMLWorker.decode_xml method"""
		return XMLWorker.decode_xml(content)

	async def fetch_content(self, file):
		"""Loads and decodes the xml scenario from test file

		Returns decoded scenario content or None, if an error occurs
		"""
		for blocking_task in as_completed([self._event_loop.run_in_executor(self._thread_executor, FileSystem.load_from, file)]):   
			file_content = await blocking_task  # Loads the xml scenario from test file
		if file_content is None:
			# Sending a scenario load error report
			self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.PARSE,
				                                 	            log="Test Error: can't parse the test file '%s'. Details: file does't exist or no permission to read it" % file,
				                                 	            success=False)))
			return
		result, content = await TestParser.decode_xml(file_content)  # Decodes the xml scenario
		if not result:
			# Sending a scenario decode error report
			self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.PARSE,
				                                 	            log="Test Error: can't parse the test file '%s'. Details: %s" % (file, content),
				                                 	            success=False)))
			return
		return content

	async def parse_test(self, file):
		"""Parses and validates the decoded xml scenario from test file

		Returns decoded and valid scenario content or None, if an error occurs
		"""
		content = await self.fetch_content(file)  # Deserialization and decoding of the test file
		if content is None:
			return
		result, reason = await self.validate_test(content)  # Validating the scenario from test file
		if not result:
		    # Sending a scenario validation error report
		    self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.PARSE,
				                                 	            log="Test Error: can't parse the test file '%s'. Details: %s" % (file, reason),
				                                 	            success=False)))
		    return
		# Sending a report on the successful parsing of the test scenario
		self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.PARSE,
				                                 	        log="File '%s' is successfully parsed" % file,
				                                 	        success=True)))
		return content

	async def main_coro(self):
		"""Creates tasks for asynchronous event loop"""
		tasks = [self.parse_test(file) for file in self.tests_files]  # Creating tasks for event loop
		# Asynchronous task execution by event loop
		for number,task in enumerate(as_completed(tasks)):
			content = await task
			# Sending the test to the Processor instance
			if content is not None:
				self.test_queue.put(Frame(Frame.TEST, Frame.Test("Test_%s_%s" % (number, content.attrib["name"]),
				                                                 self._scenario_builder.build_scenario(content))))

	def run(self):
		# Running the asynchronous event loop
		self._event_loop.run_until_complete(self.main_coro())
		# Stop the asynchronous event loop
		self._event_loop.close()
		# Send stop frames at the end of parsing of tests scenarios
		self.log_queue.put(Frame(Frame.STOP))
		self.test_queue.put(Frame(Frame.STOP))

class ScenarioValidator:
	"""Class for validating the tests files contents"""

	# Absolute path to schema for tests files
	_schema_file = dirname(__file__) + "/schema/scenario.xsd"

	def __init__(self):
		# Making the schema instance for validation of tests files contents 
		self._schema = xml.XMLSchema(xml.XML(FileSystem.load_from(ScenarioValidator._schema_file)))
	
	def validate_scenario(self, content):
		"""Validates the testing scenario contents according to the schema

		Returns result of validation and error description, if it occurs
		"""
		try:
			self._schema.assertValid(content)
		except xml.DocumentInvalid as error:
			return (False, str(error))
		return (True, None)

class XMLWorker:
	"""Static class for parsing xml contents"""
	
	@staticmethod
	def decode_xml(content):
		"""Decodes xml contents"""
		try:
			decoded_content = xml.fromstring(content)
		except xml.XMLSyntaxError as error:
			return (False, str(error))			                                 	        
		return (True, decoded_content)

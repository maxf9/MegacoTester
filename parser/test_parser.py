from parser.scenario_builder import ScenarioBuilder
from asyncio import get_event_loop, as_completed
from threading import Thread
from os.path import dirname
import lxml.etree as xml
from sys import exit

class ScenarioValidator:

	_schema_file = dirname(__file__) + "/schema/scenario.xsd"

	def __init__(self):
		self._schema = ScenarioValidator._create_schema()

	@staticmethod
	def _create_schema():
		schema_content = FileSystem.load_from(ScenarioValidator._schema_file)
		if schema_content is None:
			print("Схема '%s' не существует или нет прав доступа" % ScenarioValidator._schema_file)
			exit(1)
		try:
			schema = xml.XMLSchema(xml.XML(schema_content))
		except xml.XMLSyntaxError as error:
			print(error)
			exit(1)
		return schema
	
	def validate_scenario(self, content):
		try:
			self._schema.assertValid(content)
		except xml.DocumentInvalid as error:
			return (False, str(error))
		return (True, None)

class TestParser(Thread):

	_instance = None

	def __new__(cls, *args, **kwargs):
		if TestParser._instance is None:
			TestParser._instance = object.__new__(cls)
		return TestParser._instance
	
	def __init__(self, tests_files, test_queue, log_queue):
		super().__init__()
		self.tests_files = tests_files
		self.test_queue = test_queue
		self.log_queue = log_queue
		self._validator = ScenarioValidator()
		self._scenario_builder = ScenarioBuilder()
		self._event_loop = get_event_loop()

	@staticmethod
	async def load_file(file):
		return FileSystem.load_from(file)

	async def decode_xml(self, file_content, file_path):
		try:
			decoded_content = xml.fromstring(file_content)
		except xml.XMLSyntaxError as error:
			#Отправка отчета об ошибке декодирования файла
			self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.PARSE,
				                                 	            log="Файл '%s' имеет неправильный формат: %s" % (file_path, str(error)),
				                                 	            success=False)))
		else:
			return decoded_content

	async def fetch_content(self, file):
		#Загрузка файла тестового сценария
		file_content = await TestParser.load_file(file)
		if file_content is None:
			#Отправка отчета об ошибке загрузки файла
			self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.PARSE,
				                                 	            log="Файл '%s' не существует или нет прав доступа" % file,
				                                 	            success=False)))
			return
		#Декодирование файла тестового сценария
		content = await self.decode_xml(file_content, file)
		return content

	async def validate_test(self, content):
		return self._validator.validate_scenario(content)

	async def parse_test(self, file):
		#Десериализация и декодирование тестового сценария 
		content = await self.fetch_content(file)
		if content is None:
			return
		#Валидация тестового сценария
		result, reason = await self.validate_test(content)
		if not result:
		    #Отправка отчета об ошибке валидации файла
		    self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.PARSE,
				                                 	            log=reason,
				                                 	            success=False)))
		    return
		#Отправка отчета об успешном парсинге тестового сценария
		self.log_queue.put(Frame(Frame.REPORT, Frame.Report(Frame.Report.PARSE,
				                                 	        log="Файл '%s' успешно прошел парсинг" % file,
				                                 	        success=True)))
		return content

	async def main_coro(self):
		#Создание задач для обработчика
		tasks = [self.parse_test(file) for file in self.tests_files]
		for number,task in enumerate(as_completed(tasks)):
			content = await task
			#Постановка теста в очередь к процессору
			if content is not None:
				self.test_queue.put(Frame(Frame.TEST, Frame.Test("Test_%s_%s" % (number, content.attrib["name"]),
				                                                 self._scenario_builder.build_scenario(content))))

	def run(self):
		#Запуск обработчика событий
		self._event_loop.run_until_complete(self.main_coro())
		#Остановка обработчика событий
		self._event_loop.close()
		#Отправка стоповых кадров по завершению парсинга тестовых сценариев
		self.log_queue.put(Frame(Frame.STOP))
		self.test_queue.put(Frame(Frame.STOP))

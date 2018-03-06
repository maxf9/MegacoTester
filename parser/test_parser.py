from threading import Thread
from asyncio import get_event_loop, as_completed
import xml.etree.ElementTree as xml

class TestValidator:
	
	@staticmethod
	def validate_test(test, schema):
		pass

class TestParser(Thread):

	_instance = None
	_file_system = None
	_frame = None
	_validator = TestValidator
	_event_loop = get_event_loop()

	def __new__(cls, *args, **kwargs):
		if TestParser._instance is None:
			TestParser._instance = object.__new__(cls)
		return TestParser._instance
	
	def __init__(self, file_system, frame, tests_files, test_queue, log_queue):
		super().__init__()
		self.tests_files = tests_files
		self.test_queue = test_queue
		self.log_queue = log_queue
		TestParser._file_system = file_system
		TestParser._frame = frame

	@staticmethod
	async def load_file(file):
		return TestParser._file_system.load_from(file)

	async def decode_xml(self, raw_content, file):
		try:
			decoded_content = xml.fromstring(raw_content)
		except xml.ParseError as error_info:
			decoded_content = None
			#Отправка отчета об ошибке декодирования файла
			self.log_queue.put(TestParser._frame(TestParser._frame.REPORT, 
				                                 TestParser._frame.Report(TestParser._frame.Report.PARSE,
				                                 	                      log="Файл '%s' имеет неправильный формат: %s" % (file, str(error_info)),
				                                 	                      success=False)))
		return decoded_content

	async def fetch_content(self, file):
		#Загрузка файла тестового сценария
		raw_content = await TestParser.load_file(file)
		if raw_content is None:
			#Отправка отчета об ошибке загрузки файла
			self.log_queue.put(TestParser._frame(TestParser._frame.REPORT, 
				                                 TestParser._frame.Report(TestParser._frame.Report.PARSE,
				                                 	                      log="Файл '%s' не существует или нет прав доступа" % file,
				                                 	                      success=False)))
			return
		#Декодирование файла тестового сценария
		content = await self.decode_xml(raw_content, file)
		return content

	async def parse_test(self, file):
		#Десериализация и декодирование тестового сценария
		content = await self.fetch_content(file)
		if content is None:
			return
		#Валидация тестового сценария
		TestParser._validator.validate_test(content, schema=None)
		#Отправка отчета об успешном парсинге тестового сценария
		self.log_queue.put(TestParser._frame(TestParser._frame.REPORT, 
				                             TestParser._frame.Report(TestParser._frame.Report.PARSE,
				                                 	                  log="Файл '%s' успешно прошел парсинг" % file,
				                                 	                  success=True)))
		return content

	async def main_coro(self):
		#Создание задач для обработчика
		futures = [self.parse_test(file) for file in self.tests_files]
		for number,future in enumerate(as_completed(futures)):
			test = await future
			#Постановка теста в очередь к процессору
			if test:
				self.test_queue.put(TestParser._frame(TestParser._frame.TEST, 
					                                  TestParser._frame.Test("Test_%s_%s" % (number,test.attrib["name"].replace(" ","_")), test)))

	def run(self):
		#Запуск обработчика событий
		TestParser._event_loop.run_until_complete(self.main_coro())
		#Остановка обработчика событий
		TestParser._event_loop.close()
		#Отправка стоповых кадров по завершению парсинга тестовых сценариев
		self.log_queue.put(TestParser._frame(TestParser._frame.STOP))
		self.test_queue.put(TestParser._frame(TestParser._frame.STOP))

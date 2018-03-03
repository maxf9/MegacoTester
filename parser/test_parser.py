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
	
	def __init__(self, file_system, frame, tests_files, to_processor):
		super().__init__()
		self.tests_files = tests_files
		self.processor_queue = to_processor
		TestParser._file_system = file_system
		TestParser._frame = frame

	@staticmethod
	async def load_file(file):
		return TestParser._file_system.load_from(file)

	@staticmethod
	async def decode_xml(raw_content, file):
		try:
			decoded_content = xml.fromstring(raw_content)
		except xml.ParseError as error_info:
			decoded_content = None
			print("Ошибка декодирования файла %s. %s" % (file, str(error_info)))
		return decoded_content

	@staticmethod
	async def fetch_content(file):
		#Загрузка файла тестового сценария
		raw_content = await TestParser.load_file(file)
		if raw_content is None:
			return
		#Декодирование файла тестового сценария
		content = await TestParser.decode_xml(raw_content, file)
		return content

	async def parse_test(self, file):
		#Десериализация файла тестового сценария
		content = await TestParser.fetch_content(file)
		if content is None:
			return
		#Валидация тестового сценария
		TestParser._validator.validate_test(content, schema=None)
		#Парсинг тестового сценария
		return content

	async def main_coro(self):
		#Создание задач для обработчика
		futures = [self.parse_test(file) for file in self.tests_files]
		for number,future in enumerate(as_completed(futures)):
			test = await future
			#Постановка теста в очередь к процессору
			if test:
				self.processor_queue.put(TestParser._frame("info",data=test))

	def run(self):
		#Запуск обработчика событий
		TestParser._event_loop.run_until_complete(self.main_coro())
		#Остановка обработчика событий
		TestParser._event_loop.close()
		#Отправка стопового кадра
		self.processor_queue.put(TestParser._frame("stop"))
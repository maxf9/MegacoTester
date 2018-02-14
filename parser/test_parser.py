from threading import Thread
from asyncio import get_event_loop, as_completed

class TestParser(Thread):

	_instance = None
	_file_system = None
	_event_loop = get_event_loop()

	def __new__(cls, *args, **kwargs):
		if TestParser._instance is None:
			TestParser._instance = object.__new__(cls)
		return TestParser._instance
	
	def __init__(self, file_system, tests_files, to_processor):
		super().__init__()
		self.tests_files =  tests_files
		self.processor_queue = to_processor
		TestParser._file_system = file_system

	@staticmethod
	async def load_file(file):
		raw_content = TestParser._file_system.load_from(file)
		if raw_content is None:
			TestParser.load_file.cancel()
		return raw_content

	@staticmethod
	async def decode_xml(raw_content):
		pass

	@staticmethod
	async def fetch_content(file):
		#Загрузка файла тестового сценария
		raw_content = await TestParser.load_file(file)
		#Декодирование файла тестового сценария
		content = await TestParser.decode_xml(raw_content)
		return content

	async def parse_test(self, file):
		#Десериализация файла тестового сценария
		content = await TestParser.fetch_content(file)
		#Валидация теста
		pass
		#Парсинг теста
		test = None
		return test

	async def main_coro(self):
		#Создание задач для обработчика
		futures = [self.parse_test(file) for file in self.tests_files]
		for future in as_completed(futures):
			test = await future
			#Постановка результата выполнения задачи в очередь к процессору
			self.processor_queue.put(test, block=False)

	def run(self):
		#Запуск обработчика событий
		TestParser._event_loop.run_until_complete(self.main_coro())
		#Остановка обработчика событий
		TestParser._event_loop.close()
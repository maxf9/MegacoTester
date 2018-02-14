from threading import Thread
from asyncio import get_event_loop, as_completed, sleep

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
	async def load_content(file):
		return TestParser._file_system.load_from(file)

	@staticmethod
	async def decode_xml(raw_content):
		pass

	async def parse_test(self, file):
		#Десериализация файла тестового сценария
		raw_content = await TestParser.load_content(file)
		#Декодирование файла тестового сценария
		content = await TestParser.decode_xml(raw_content)
		#Валидация теста
		pass
		#Парсинг теста
		pass

	async def main_coro(self):
		futures = [self.parse_test(file) for file in self.tests_files]
		for future in as_completed(futures):
			test = await future
			#print(test)

	def run(self):
		#Запуск обработчика событий
		TestParser._event_loop.run_until_complete(self.main_coro())
		#Остановка обработчика событий
		TestParser._event_loop.close()
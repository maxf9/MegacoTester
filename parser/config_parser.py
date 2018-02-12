from sys import exit, exc_info
from os.path import dirname
import json

class ConfigParser:

	_instance = None
	_validator = None
	_file_system = None
	_schema_file = dirname(__file__) + "/schema/config.json"

	def __new__(cls, *args):
		if ConfigParser._instance is None:
			ConfigParser._instance = object.__new__(cls)
		return ConfigParser._instance

	def __init__(self, file_system):
		ConfigParser._file_system = file_system

	@staticmethod
	def decode_json(json_content, file_path):
		try:
			decoded_content = json.loads(json_content)
		except json.decoder.JSONDecodeError:
			print("Ошибка декодирования файла %s. %s" % (file_path, exc_info()[1]))
			exit(1)
		return decoded_content

	@staticmethod
	def fetch_content(json_file):
		#Загрузка содержимого файла
		raw_content = ConfigParser._file_system.load_from(json_file)
		#Проверка успешного выполнения загрузки содержимого файла
		if raw_content is None:
			print("Не удалось загрузить содержимое файла %s. Файла не существует или нет прав на его чтение" % json_file)
			exit(1)
		#Декодирование файла
		content = ConfigParser.decode_json(raw_content, file_path=json_file)
		return content

	def parse_config(self, config_file):
		config = ConfigParser.fetch_content(config_file)
		schema = ConfigParser.fetch_content(ConfigParser._schema_file)
		
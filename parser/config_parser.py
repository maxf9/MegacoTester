from sys import exit, exc_info
from os.path import dirname
import json

class ConfigValidator:
	
	@staticmethod
	def validate_config(config, schema):
		pass

class ConfigParser:

	_instance = None
	_validator = ConfigValidator
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
		#Десериализация схемы и файла конфигурации
		raw_config = ConfigParser.fetch_content(config_file)
		schema = ConfigParser.fetch_content(ConfigParser._schema_file)
		#Валидация конфигурационного файла при помощи схемы
		ConfigParser._validator.validate_config(raw_config, schema)
		#Сборка объекта класса Config на основе конфигурационного файла
		return Config(raw_config)

class Config:

	class Node:
		
		def __init__(self):
			self.id = None
			self.info = None
			self.ip_address = None
			self.port = None
			self.mid = None
			self.encoding = None
			self.terms = None

	class Connection:
		
		def __init__(self):
			self.id = None
			self.info = None
			self.from_node = None
			self.to_node = None
	
	def __init__(self, raw_config):
		self.log_dir = None
		self.globals = None
		self.dialplans = None
		self.nodes = None
		self.connections = None

	def __str__(self):
		return "Config object"


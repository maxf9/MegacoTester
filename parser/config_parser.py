from jsonschema import Draft4Validator
from parser.config import Config
from sys import exit, exc_info
from os.path import dirname
import json

class ConfigValidator:
	
	@staticmethod
	def print_errors(errors):
		for error in errors:
			print(error)

	@staticmethod
	def is_unique_identiers(**sections):
		indicator = True
		for name,section in sections.items():
			identifiers = set()
			for item in section:
				if item["id"] not in identifiers:
					identifiers.add(item["id"])
				else:
					indicator = False
					print("Объект '{name}' секции '{section}' имеет неуникальный идентификатор: {id}".format(name=item["name"],section=name,id=item["id"]))
		return indicator

	@staticmethod
	def is_acceptable_connections(connections):
		indicator = True
		for connection in connections:
			if connection["from_node"] == connection["to_node"]:
				indicator = False
				print("Connection '{id}' имеет одинаковые идентификаторы 'from_node' и 'to_node'".format(id=connection["id"]))
		return indicator

	@staticmethod 
	def validate_config(config, schema):
		errors = sorted(Draft4Validator(schema).iter_errors(config), key=lambda e: e.path)
		#Проверка наличия ошибок при валидации
		if errors:
			ConfigValidator.print_errors(errors)
			exit(1)
		#Проверка существования и доступности директории для логов
		if not ConfigParser.file_system.is_acceptable_directory(config["LogDirectory"]):
			print("Directory \"%s\" is not acceptable log directory" % config["LogDirectory"])
			exit(1)
		#Проверка уникальности идентификаторов
		if not ConfigValidator.is_unique_identiers(Nodes=config["Nodes"], Connections=config["Connections"]):
			exit(1)
		#Проверка на отсутствие вырожденных соединений
		if not ConfigValidator.is_acceptable_connections(config["Connections"]):
			exit(1)

class ConfigParser:

	_instance = None
	_validator = ConfigValidator
	file_system = None
	_schema_file = dirname(__file__) + "/schema/config.json"

	def __new__(cls, *args, **kwargs):
		if ConfigParser._instance is None:
			ConfigParser._instance = object.__new__(cls)
		return ConfigParser._instance

	def __init__(self, file_system):
		ConfigParser.file_system = file_system

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
		raw_content = ConfigParser.file_system.load_from(json_file)
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
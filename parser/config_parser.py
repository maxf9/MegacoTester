from parser.config_builder import ConfigBuilder
from jsonschema import Draft4Validator
from os.path import dirname
from sys import exit
import json

def decode_json(content, file_path):
	try:
		decoded_content = json.loads(content)
	except json.decoder.JSONDecodeError as error:
		print("Ошибка декодирования файла %s. %s" % (file_path, error))
		exit(1)
	return decoded_content

def fetch_content(file):
	#Загрузка содержимого файла
	file_content = FileSystem.load_from(file, binary=False)
	#Проверка успешного выполнения загрузки содержимого файла
	if file_content is None:
		print("Не удалось загрузить содержимое файла %s. Файла не существует или нет прав на его чтение" % file)
		exit(1)
	#Декодирование содержимого файла
	content = decode_json(file_content, file)
	return content

class ConfigValidator:

	_schema_file = dirname(__file__) + "/schema/config.json"

	def __init__(self):
		self._schema = fetch_content(ConfigValidator._schema_file)

	def validate_config(self, content):
		errors = sorted(Draft4Validator(self._schema).iter_errors(content), key=lambda e: e.path)
		#Проверка наличия ошибок при валидации
		if errors:
			ConfigValidator.print_errors(errors)
			exit(1)
		#Проверка существования и доступности директории для логов
		if not FileSystem.is_acceptable_directory(content["LogDirectory"]):
			print("Directory \"%s\" is not acceptable log directory" % content["LogDirectory"])
			exit(1)
		#Проверка уникальности идентификаторов
		if not ConfigValidator.is_unique_identiers(Nodes=content["Nodes"], Connections=content["Connections"]):
			exit(1)
		#Проверка на отсутствие вырожденных соединений
		if not ConfigValidator.is_acceptable_connections(content["Connections"]):
			exit(1)

	@staticmethod
	def is_unique_identiers(**sections):
		valid_indicator = True
		for name,section in sections.items():
			identifiers = set()
			for item in section:
				if item["id"] not in identifiers:
					identifiers.add(item["id"])
				else:
					valid_indicator = False
					print("Объект '%s' секции '%s' имеет неуникальный идентификатор: %s" % (item["name"], name, item["id"]))
		return valid_indicator

	@staticmethod
	def is_acceptable_connections(connections):
		valid_indicator = True
		for connection in connections:
			if connection["from_node"] == connection["to_node"]:
				valid_indicator = False
				print("Connection '%s' имеет одинаковые идентификаторы 'from_node' и 'to_node'" % connection["id"])
		return valid_indicator

	@staticmethod
	def print_errors(errors):
		for error in errors:
			print(error)

class ConfigParser:

	_instance = None

	def __new__(cls, *args, **kwargs):
		if ConfigParser._instance is None:
			ConfigParser._instance = object.__new__(cls)
		return ConfigParser._instance

	def __init__(self):
		self._validator = ConfigValidator()
		self._config_builder = ConfigBuilder()

	def parse_config(self, config_file):
		#Десериализация и декодирование файла конфигурации
		content = fetch_content(config_file)
		#Валидация конфигурационного файла
		self._validator.validate_config(content)
		#Сборка объекта класса Config на основе конфигурационного файла
		return self._config_builder.build_config(content)
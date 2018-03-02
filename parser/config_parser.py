from sys import exit, exc_info
from os.path import dirname
from jsonschema import Draft4Validator
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

class Config:

	_instance = None

	def __new__(cls, *args, **kwargs):
		if Config._instance is None:
			Config._instance = object.__new__(cls)
		return Config._instance
	
	def __init__(self, raw_config):
		self.log_dir = raw_config["LogDirectory"]
		self.globals = raw_config["Globals"]
		self.dialplans = raw_config["Dialplans"]
		self.nodes = tuple(Config.create_component(fabric, type="Node") for fabric in raw_config["Nodes"])
		self.connections = tuple(Config.create_component(fabric, type="Connection") for fabric in raw_config["Connections"])

	class Node:

		_custom_fields = ("name","mid","encoding","terms","network_buffer")
		
		def __init__(self, fabric):
			self.id = fabric["id"]
			self.name = None
			self.ip_address = fabric["ip_address"]
			self.port = fabric["port"]
			self.mid = "[%s]:%s" % (self.ip_address, self.port)
			self.encoding = "full_text"
			self.terms = tuple()
			self.network_buffer = 15000
			self.customize(fabric)

		def customize(self, fabric):
			for field in Config.Node._custom_fields:
				try:
					if field == "name":
						self.name = fabric[field]
					elif field == "mid":
						self.mid = fabric[field]
					elif field == "encoding":
						self.encoding = fabric[field]
					elif field == "terms":
						self.terms = tuple(fabric[field])
					elif field == "network_buffer":
						self.network_buffer = fabric[field]
				except KeyError:
					pass

		def __str__(self):
			return "Node: %s" % self.id

		def __repr__(self):
			return "Node: %s" % self.id

	class Connection:
		
		def __init__(self, fabric):
			self.id = fabric["id"]
			self.name = None
			self.from_node = fabric["from_node"]
			self.to_node = fabric["to_node"]
			self.customize(fabric)

		def customize(self, fabric):
			try:
				self.name = fabric["name"]
			except KeyError:
				pass

		def __str__(self):
			return "Connection: %s" % self.id

		def __repr__(self):
			return "Connection: %s" % self.id

	@staticmethod
	def create_component(fabric, type):
		component = None
		if type == "Node":
			component = Config.Node(fabric)
		elif type == "Connection":
			component = Config.Connection(fabric)
		return component

	def __str__(self):
		return "Config object"


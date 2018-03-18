class Config:

	_instance = None
	_custom_fields = ("Globals","Dialplans")

	def __new__(cls, *args, **kwargs):
		if Config._instance is None:
			Config._instance = object.__new__(cls)
		return Config._instance
	
	def __init__(self, raw_config):
		self.log_dir = raw_config["LogDirectory"]
		self.globals = {}
		self.dialplans = []
		self.nodes = tuple(Config._create_component(fabric, type="Node") for fabric in raw_config["Nodes"])
		self.connections = tuple(Config._create_component(fabric, type="Connection") for fabric in raw_config["Connections"])
		self._customize(raw_config)

	@staticmethod
	def _create_component(fabric, type):
		component = None
		if type == "Node":
			component = Config.Node(fabric)
		elif type == "Connection":
			component = Config.Connection(fabric)
		return component

	def _customize(self, raw_config):
		for field in Config._custom_fields:
			try:
				if field == "Globals":
					self.globals = raw_config[field]
				elif field == "Dialplans":
					self.dialplans = raw_config[field]
			except KeyError:
				pass

	def __str__(self):
		return "Config object"

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
			self._customize(fabric)

		def _customize(self, fabric):
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
			return self.__str__()

	class Connection:
		
		def __init__(self, fabric):
			self.id = fabric["id"]
			self.name = None
			self.from_node = fabric["from_node"]
			self.to_node = fabric["to_node"]
			self._customize(fabric)

		def _customize(self, fabric):
			try:
				self.name = fabric["name"]
			except KeyError:
				pass

		def __str__(self):
			return "Connection: %s" % self.id

		def __repr__(self):
			return self.__str__()

class ConfigBuilder:

	def build_config(self, content):
		return Config(content)
class ConfigBuilder:
	"""Class for building the Config instance from validated contents of the configuration file"""

	_instance = None

	def __new__(cls, *args, **kwargs):
		if ConfigBuilder._instance is None:
			ConfigBuilder._instance = object.__new__(cls)
		return ConfigBuilder._instance

	def __init__(self):
		self._config = Config()
		self._makers = self._define_makers()

	def _define_makers(self):
		return {"LogDirectory" : self._make_log_directory,
		        "Globals" : self._make_globals,
		        "Dialplans" : self._make_dialplans,
		        "Nodes" : self._make_nodes,
		        "Connections" : self._make_connections}

	@staticmethod
	def _build_node(fabric):
		node = Config.Node(fabric["id"], fabric["ip_address"], fabric["port"])
		for field in ("name", "mid", "encoding", "terms", "network_buffer"):
			try:
				if field == "name":
					node.name = fabric[field]
				elif field == "mid":
					node.mid = fabric[field]
				elif field == "encoding":
					node.encoding = fabric[field]
				elif field == "terms":
					node.terms = tuple(fabric[field])
				elif field == "network_buffer":
					node.network_buffer = fabric[field]
			except KeyError:
				pass
		return node

	@staticmethod
	def _build_connection(fabric):
		connection = Config.Connection(fabric["id"], fabric["from_node"], fabric["to_node"])
		try:
			connection.name = fabric["name"]
		except KeyError:
			pass
		return connection

	def _make_log_directory(self, sample):
		self._config.log_dir = sample

	def _make_globals(self, sample):
		self._config.globals = sample

	def _make_dialplans(self, sample):
		self._config.dialplans = sample

	def _make_nodes(self, sample):
		self._config.nodes = tuple(ConfigBuilder._build_node(fabric) for fabric in sample)

	def _make_connections(self, sample):
		self._config.connections = tuple(ConfigBuilder._build_connection(fabric) for fabric in sample)

	def build_config(self, content):
		for component in content:
			self._makers[component](content[component])
		return self._config

class Config:

	def __init__(self):
		self.log_dir = None
		self.globals = {}
		self.dialplans = []
		self.nodes = None
		self.connections = None

	class Node:

		def __init__(self, nid, ip_address, port):
			self.id = nid
			self.name = ""
			self.ip_address = ip_address
			self.port = port
			self.mid = "[%s]:%s" % (self.ip_address, self.port)
			self.encoding = "full_text"
			self.terms = tuple()
			self.network_buffer = 15000

	class Connection:

		def __init__(self, cid, from_node, to_node):
			self.id = cid
			self.name = ""
			self.from_node = from_node
			self.to_node = to_node
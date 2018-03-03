from multiprocessing import Process
from processor.network import NetworkAdapter
from sys import exit

class Interpreter(Process):

	_instance = None
	_variables_tree = None

	@staticmethod
	def _define_command_handlers():
		return { "Variables" : Interpreter._handle_variables,
		         "send" : Interpreter._handle_send,
		         "recv" : Interpreter._handle_recv,
		         "action" : Interpreter._handle_action }

	def __new__(cls, *args, **kwargs):
		if Interpreter._instance is None:
			Interpreter._instance = object.__new__(cls)
		return Interpreter._instance

	def __init__(self, config, to_processor):
		super().__init__()
		self.processor_queue = to_processor
		self._command_handlers = Interpreter._define_command_handlers()
		self._network_adapters = Interpreter._configure_adapters(config.connections, config.nodes)
		self._routes = Interpreter._configure_routes(config.connections)
		Interpreter._build_variables_tree(config)

	@staticmethod
	def _build_variables_tree(config):
		pass

	@staticmethod
	def fetch_item(id, items):
		for item in items:
			if item.id == id:
				break
		else:
			print("Объект 'Node' с id=%s не найден в конфигурационном файле" % id)
			exit(1)
		return item

	@staticmethod
	def _configure_adapters(connections, nodes):
		config_data = {}
		for connection in connections:
			if connection.from_node not in config_data:
				config_data[connection.from_node] = [connection.id]
			else:
				config_data[connection.from_node] += [connection.id]
		network_adapters = {}
		for key,value in config_data.items():
			network_adapters[tuple(value)] = NetworkAdapter(Interpreter.fetch_item(key, nodes),
			*[Interpreter.fetch_item(Interpreter.fetch_item(i,connections).to_node, nodes) for i in value])
		return network_adapters

	@staticmethod
	def _configure_routes(connections):
		return dict([(connection.id, connection.to_node) for connection in connections])

	@staticmethod
	def _handle_variables(instructions):
		pass

	@staticmethod
	def _handle_recv(instructions):
		pass

	@staticmethod
	def _handle_send(instructions):
		pass

	@staticmethod
	def _handle_action(instructions):
		pass

	def run(self):
		pass
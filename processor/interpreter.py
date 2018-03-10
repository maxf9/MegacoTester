from processor.network import NetworkAdapter
from re import findall, search
from sys import exit

class Interpreter:

	_instance = None
	_global_variables = None

	def _define_command_handlers(self):
		return { "variables" : self._handle_variables,
		         "send" : self._handle_send,
		         "recv" : self._handle_recv,
		         "action" : Interpreter._handle_action }

	def __new__(cls, *args, **kwargs):
		if Interpreter._instance is None:
			Interpreter._instance = object.__new__(cls)
		return Interpreter._instance

	def __init__(self, config):
		self._command_handlers = self._define_command_handlers()
		self._network_adapters = Interpreter._configure_adapters(config.connections, config.nodes)
		self._routes = Interpreter._configure_routes(config.connections)
		self._local_variables = None
		Interpreter._build_global_variables_tree(config)

	@staticmethod
	def _build_global_variables_tree(config):
		Interpreter._global_variables = config.globals

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

	def stop_all_network_adapters(self):
		for network_adapter in self._network_adapters.values():
			network_adapter.close()

	@staticmethod
	def _configure_routes(connections):
		return dict([(connection.id, connection.to_node) for connection in connections])

	def _get_network_adapter(self, connection):
		for connections in self._network_adapters:
			if connection in connections:
				network_adapter = self._network_adapters[connections]
				return network_adapter

	@staticmethod
	def _replace_global_variables(message):
		raw_variables = set(findall(r"\[\$\$[A-Za-z0-9_]+\]", message))
		for raw_variable in raw_variables:
			variable = search(r"[A-Za-z0-9_]+", raw_variable).group(0)
			if variable in Interpreter._global_variables:
				message = message.replace(raw_variable, Interpreter._global_variables[variable])
			else:
				return (False, "Переменная '%s' не объявлена в глобальном пространстве имен\n" % variable)
		return (True, message)

	def _replace_local_variables(self, message):
		raw_variables = set(findall(r"\[\$[A-Za-z0-9_]+\]", message))
		for raw_variable in raw_variables:
			variable = search(r"[A-Za-z0-9_]+", raw_variable).group(0)
			if variable in self._local_variables:
				message = message.replace(raw_variable, self._local_variables[variable])
			else:
				return (False, "Переменная '%s' не объявлена в локальном пространстве имен\n" % variable)
		return (True, message)

	def _replace_variables(self, raw_message):
		#Замена глобальных переменных
		result, data = Interpreter._replace_global_variables(raw_message)
		if not result: return (False, data)
		#Замена локальных переменных
		result, data = self._replace_local_variables(data)
		if not result: return (False, data)
		return (True, data)

	def _handle_variables(self, instruction):
		self._local_variables.update(instruction.attrib)
		return (True, "Переменные %s объявлены в локальном пространстве имен\n" % str(self._local_variables))

	def _handle_recv(self, instruction):
		connection = int(instruction.attrib["connection"])
		#Поиск сетевого адаптера по идентификатору соединения
		network_adapter = self._get_network_adapter(connection)
		if network_adapter is None:
			return (False, "Recv: неправильный идентификатор соединения '%s'\n" % connection)
		#Прием сообщения сетевым адаптером
		result, log, data = network_adapter.recv(self._routes[connection], timeout=int(instruction.attrib["timeout"]))
		return(result, log)

	def _handle_send(self, instruction):
		connection = int(instruction.attrib["connection"])
		#Поиск сетевого адаптера по идентификатору соединения
		network_adapter = self._get_network_adapter(connection)
		if network_adapter is None:
			return (False, "Send: неправильный идентификатор соединения '%s'\n" % connection)
		#Подстановка значений переменных в сообщение
		result, message = self._replace_variables(instruction.text)
		if not result:
			return (False, message)
		#Отправка сообщения удаленному узлу
		return network_adapter.send(message, to_node=self._routes[connection])

	@staticmethod
	def _handle_action(instruction):
		return (True, "")

	def execute(self, scenario):
		log = ""
		#Установка локального пространства имен
		self._local_variables = {}
		#Выполнение инструкций сценария
		for instruction in scenario:
			try:
				instruction_result, instruction_log = self._command_handlers[instruction.tag](instruction)
				log += instruction_log
				if not instruction_result:
					return (False, log)
			except KeyError:
				return (False, log + "Неверная инструкция '%s'" % instruction.tag)
		return (True, log)
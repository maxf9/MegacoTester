from processor.network import NetworkAdapter
from time import sleep, strftime
from re import findall, compile
from threading import Event
from sys import exit

class ScenarioInterpreter:

	_instance = None
	_global_variables = None

	def _define_command_handlers(self):
		return { "Define" : self._handle_define,
		         "Send" : self._handle_send,
		         "Recv" : self._handle_recv,
		         "Actions" : self._handle_actions,
		         "Catch" : self._handle_catch,
		         "Compare" : self._handle_compare,
		         "Assign" : self._handle_assign,
		         "Print" : self._handle_print,
		         "Exit" : self._handle_exit,
		         "Nop" : self._handle_nop,
		         "Pause" : ScenarioInterpreter._handle_pause }

	def __new__(cls, *args, **kwargs):
		if ScenarioInterpreter._instance is None:
			ScenarioInterpreter._instance = object.__new__(cls)
		return ScenarioInterpreter._instance

	def __init__(self, config):
		self._command_handlers = self._define_command_handlers()
		self._network_adapters = ScenarioInterpreter._configure_adapters(config.connections, config.nodes)
		self._routes = ScenarioInterpreter._configure_routes(config.connections)
		self._successfull_exit_flag = Event()
		self._local_variables = None
		self._test_log = None
		self._test_dump = None
		ScenarioInterpreter._build_global_variables_tree(config)

	@staticmethod
	def _build_global_variables_tree(config):
		ScenarioInterpreter._global_variables = config.globals

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
			network_adapters[tuple(value)] = NetworkAdapter(ScenarioInterpreter.fetch_item(key, nodes),
			*[ScenarioInterpreter.fetch_item(ScenarioInterpreter.fetch_item(i,connections).to_node, nodes) for i in value])
		return network_adapters

	def stop_all_network_adapters(self):
		for network_adapter in self._network_adapters.values():
			network_adapter.close()

	@staticmethod
	def _configure_routes(connections):
		return dict([(connection.id, connection.to_node) for connection in connections])

	def _get_network_adapter(self, connection):
		"""Searches for and returns an instance of the network adapter by it's connection identifier"""
		for connections in self._network_adapters:
			if connection in connections:
				return self._network_adapters[connections]

	@staticmethod
	def _replace_global_variables(string):
		"""Replaces global variables in the string with their values

		Returns the changing result, error reason and string with replased variables (if result is True, None otherwise)
		"""
		for variable in set([var[3:-1] for var in findall(r"\[\$\$[A-Za-z0-9_]+\]", string)]):                    # Forming the set of global variables found in a string
			if variable in ScenarioInterpreter._global_variables:
				string = string.replace("[$$" + variable + "]", ScenarioInterpreter._global_variables[variable])  # Replacing a global variable with its value
			else:
				return (False, "Variable '%s' does not exist in the global namespace" % variable, None)
		return (True, None, string)

	def _replace_local_variables(self, string):
		"""Replaces local variables in the string with their values

		Returns the changing result, error reason and string with replased variables (if result is True, None otherwise)
		"""
		for variable in set([var[2:-1] for var in findall(r"\[\$[A-Za-z0-9_]+\]", string)]):     # Forming the set of local variables found in a string
			if variable in self._local_variables:
				string = string.replace("[$" + variable + "]", self._local_variables[variable])  # Replacing a local variable with its value
			else:
				return (False, "Variable '%s' does not exist in the local namespace" % variable, None)
		return (True, None, string)

	def _replace_variables(self, string):
		"""Replaces local and global variables in the string with their values

		Returns the changing result, error reason and string with replased variables (if result is True, None otherwise)
		"""
		success, reason, string = self._replace_local_variables(string)                  # Replacing variables from the local namespace
		if not success:
			return (False, reason, None)
		success, reason, string = ScenarioInterpreter._replace_global_variables(string)  # Replacing variables from	the global namespace
		if not success:
			return (False, reason, None)
		return (True, None, string)

	def _handle_define(self, instruction):
		"""Executes the define instruction of the test scenario

		Adds users variables to local scenario namespace
		"""
		self._local_variables.update(instruction.variables)
		self._test_log += strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\t[Define]  User variables '%s' were successfully defined in the local namespace\n\n" % ", ".join(instruction.variables.keys())
		return True

	def _handle_recv(self, instruction):
		"""Executes the recv instruction of the test scenario

		Returns True, if instruction has successfully completed or False otherwise 
		"""
		# Searching for a network adapter by connection identifier
		network_adapter = self._get_network_adapter(instruction.connection)
		if network_adapter is None:
			self._test_log += strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\t[Recv]    Value '%s' is nonexistent connection identifier\n" % instruction.connection
			return False
		# Receiving a message from a connection
		success, recv_log, data = network_adapter.recv(self._routes[instruction.connection], timeout=instruction.timeout)
		self._test_log += strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\t[Recv]    " + recv_log + "\n"
		if not success:
			return False
		# Executing nested instructions
		if not self._handle_actions(instruction.instructions, data):
			return False
		return True

	def _handle_send(self, instruction):
		#Поиск сетевого адаптера по идентификатору соединения
		network_adapter = self._get_network_adapter(instruction.connection)
		if network_adapter is None:
			self._test_log += "Send: неправильный идентификатор соединения '%s'\n" % instruction.connection
			return (False, )
		#Подстановка значений переменных в сообщение
		result, message = self._replace_variables(instruction.text)
		if not result:
			return (False, message)
		#Отправка сообщения удаленному узлу
		return network_adapter.send(message, to_node=self._routes[connection])

	def _handle_actions(self, instructions, data=None):
		"""Executes instructions from the action block

		If the command result is False, the handler terminates the scenario execution and returns False
		Returns True otherwise 
		"""
		for instruction in instructions:
			if not self._command_handlers[instruction.__class__.__name__](instruction, data):
				return False
		return True

	def _handle_catch(self, instruction, data):
		#Получение значений атрибутов инструкции
		regexp = compile(instruction.attrib["regexp"])
		overlap = int(instruction.attrib["overlap"])
		check_it = True if instruction.attrib["check_it"] == "true" else False
		variables = instruction.attrib["assign_to"].split(",")
		#Нахождение всех возможных совпадений с регулярным выражением
		values = regexp.findall(data)
		#Обработка результатов и запись переменных в локальное пространство имен
		if not values:
			if check_it:
				return (False, "По регулярному выражению '%s' не найдено совпадений\n" % regexp)
			else:
				for variable in variables:
				    self._local_variables[variable] = ""
		elif overlap < len(values):
			overlapped = values[overlap]
			if type(overlapped) == str:
				for variable in variables:
					self._local_variables[variable] = overlapped
			else:
				for variable in variables:
					pass #запись множества значений в несколько переменных
		else:
			return (False, "Невозможно извлечь совпадение по данному полю overlap: '%s'\n" % overlap)
		return (True, "Действие 'catch' успешно обработано\n")

	@staticmethod
	def _handle_pause(instruction):
		timeout = int(instruction.attrib["timeout"]) / 1000
		sleep(timeout)
		return (True, "Пауза на %s миллисекунд\n" % timeout)

	def _handle_nop(self, instructions):
		log = ""
		#Исполнение вложенных инструкций
		for instruction in instructions:
			result, action_log = self._command_handlers[instruction.tag](instruction)
			log += action_log
			if not result:
				return (False, log)
		return (True, log)

	def _handle_compare(self, instruction, *args):
		#Получение значений атрибутов инструкции
		result, first_group = self._replace_variables(instruction.attrib["first"])
		if not result:
			return (False, first_group)
		result, second_group = self._replace_variables(instruction.attrib["second"])
		if not result:
			return (False, second_group)
		#Формирование групп значений переменных для попарного сравнения
		first_group = first_group.split(",")
		second_group = second_group.split(",")
		#Группы сравнения должны иметь одинаковое количество переменных
		if len(first_group) != len(second_group):
			return (False, "Группы сравнения имеют разное количество переменных\n")
		#Попарное сравнение значений переменных
		log = ""
		for i in range(len(first_group)):
			if first_group[i] != second_group[i]:
				#Выполнение вложенных инструкций при неравенстве значений переменных
				for action in instruction:
					result, action_log = self._command_handlers[action.tag](action)
					log += action_log
					if not result:
						return (False, "Сравнение переменных неуспешно\n" + log)
				return (False, "Сравнение переменных неуспешно\n" + log)
		return (True, "Сравнение переменных прошло успешно\n")

	def _handle_assign(self, instruction, *args):
		"""Executes the assign instruction of the test scenario

		Returns True, if instruction has successfully completed or False otherwise
		"""
		success, reason, values = self._replace_variables(instruction.values)     # Changing variables to their values
		if not success:
			self._test_log += strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\t[Assign]  " + reason + "\n"
			return False
		variables, values = instruction.to.split(","), values.split(",")          # Splitting the strings into words
		if len(variables) != len(values):
			self._test_log += strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\t[Assign]  The number of assignable values '%s' is not equal to the number of declared variables '%s'\n" % (len(values), len(variables))
			return False
		for number, variable in enumerate(variables):                             # Declaring variables in the local scenario namespace
			self._local_variables[variable] = values[number]
		self._test_log += strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\t[Assign]  User variables '%s' were successfully defined in the local namespace\n" % ", ".join(variables)
		print(self._local_variables)
		print(ScenarioInterpreter._global_variables)
		return True

	def _handle_print(self, instruction, *args):
		result, text = self._replace_variables(instruction.attrib["text"])
		if not result:
			return (False, text + "\n")
		return (True, text + "\n")

	def _handle_exit(self, instruction, *args):
		#Получение значений атрибутов инструкции
		success = True if instruction.attrib["success"] == "true" else False
		result, info = self._replace_variables(instruction.attrib["info"])
		if not result:
			return (False, info + "\n")
		if success:
			self._successfull_exit_flag.set()
		return (False, info + "\n")

	def execute(self, scenario):
		"""Executes the test scenario

		Returns the execution result, collected test log and dump of messages
		"""
		self._local_variables = {}             # Setting up a local scenario namespace
		self._successfull_exit_flag.clear()    # Resetting of the successful exit flag
		self._test_log = self._test_dump = ""  # Initializing the test log and dump
		# Execution of the scenario instructions
		for instruction in scenario:
			if not self._command_handlers[instruction.__class__.__name__](instruction):
				# Test result is True, if the exit status was successful 
				if self._successfull_exit_flag.isSet():
					return (True, self._test_log, self._test_dump)
				else:
					return (False, self._test_log, self._test_dump)
		return (True, self._test_log, self._test_dump)
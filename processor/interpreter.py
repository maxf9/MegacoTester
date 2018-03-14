from processor.network import NetworkAdapter
from re import findall, search, compile
from threading import Event
from time import sleep
from sys import exit

class Interpreter:

	_instance = None
	_global_variables = None

	def _define_command_handlers(self):
		return { "variables" : self._handle_variables,
		         "send" : self._handle_send,
		         "recv" : self._handle_recv,
		         "actions" : self._handle_actions,
		         "catch" : self._handle_catch,
		         "compare" : self._handle_compare,
		         "assign" : self._handle_assign,
		         "print" : self._handle_print,
		         "exit" : self._handle_exit,
		         "nop" : self._handle_nop,
		         "pause" : Interpreter._handle_pause }

	def __new__(cls, *args, **kwargs):
		if Interpreter._instance is None:
			Interpreter._instance = object.__new__(cls)
		return Interpreter._instance

	def __init__(self, config):
		self._command_handlers = self._define_command_handlers()
		self._network_adapters = Interpreter._configure_adapters(config.connections, config.nodes)
		self._routes = Interpreter._configure_routes(config.connections)
		self._local_variables = None
		self._correct_exit_flag = Event()
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
		#Получение идентификатора соединения по атрибуту объекта
		connection = int(instruction.attrib["connection"])
		#Поиск сетевого адаптера по идентификатору соединения
		network_adapter = self._get_network_adapter(connection)
		if network_adapter is None:
			return (False, "Recv: неправильный идентификатор соединения '%s'\n" % connection)
		#Прием сообщения сетевым адаптером
		result, log, data = network_adapter.recv(self._routes[connection], timeout=int(instruction.attrib["timeout"]))
		if not result:
			return (False, log)
		#Исполнение вложенных инструкций
		for action in instruction:
			result, action_log = self._command_handlers[action.tag](action, data)
			log += action_log
			if not result:
				return (False, log)
		return(True, log)

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

	def _handle_actions(self, instructions, data=None):
		log = ""
		#Исполнение вложенных инструкций
		for instruction in instructions:
			result, action_log = self._command_handlers[instruction.tag](instruction, data)
			log += action_log
			if not result:
				return (False, log)
		return (True, log)

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
		#Получение значений атрибутов инструкции
		result, value = self._replace_variables(instruction.attrib["value"])
		if not result:
			return (False, value)
		variables = instruction.attrib["to"].split(",")
		#Объявление переменных в локальном пространстве имен
		for variable in variables:
			self._local_variables[variable] = value
		return (True, "Переменные успешно объявлены в локальном пространстве имен\n")

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
			self._correct_exit_flag.set()
		return (False, info + "\n")

	def execute(self, scenario):
		log = ""
		#Установка локального пространства имен
		self._local_variables = {}
		#Сброс флага корректного корректного выхода
		self._correct_exit_flag.clear()
		#Выполнение инструкций сценария
		for instruction in scenario:
			try:
				instruction_result, instruction_log = self._command_handlers[instruction.tag](instruction)
				log += instruction_log
				if not instruction_result:
					if self._correct_exit_flag.isSet():
						return (True, log)
					else:
						return (False, log)
			except KeyError:
				return (False, log + "Неверная инструкция '%s'\n" % instruction.tag)
		return (True, log)
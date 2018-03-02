from multiprocessing import Process
from processor.network import Network

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
		Interpreter.build_variables_tree(config)

	@staticmethod
	def build_variables_tree(config):
		pass

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
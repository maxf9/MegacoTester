from multiprocessing import Process

class Interpreter(Process):

	_instance = None

	def __new__(cls, *args, **kwargs):
		if Interpreter._instance is None:
			Interpreter._instance = object.__new__(cls)
		return Interpreter._instance

	def __init__(self):
		super().__init__()
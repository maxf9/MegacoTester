from random import randint
from time import strftime

class Megaco:

	def __init__(self):
		self._generators = self._define_generators()

	def _define_generators(self):
		return {
		    "transaction_id" : Megaco._generate_uint32,
		    "context_id" : Megaco._generate_uint32,
		    "request_id" : Megaco._generate_uint32,
		    "timestamp" : Megaco._generate_timestamp
		}

	@staticmethod
	def _generate_uint32():
		return str(randint(1, 4294967295))

	@staticmethod
	def _generate_timestamp(): # per ISO 8601:1988
		return strftime("%Y%m%dT%H%M%S00")

	def generate_value(self, variable):
		if variable in self._generators:
			return self._generators[variable]()
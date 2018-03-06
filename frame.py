class Frame:

	STOP, TEST, REPORT = range(3)

	def __init__(self, header, payload=None):
		self.header = header
		self.payload = payload

	def __str__(self):
		if self.header == Frame.STOP:
			return "STOP Frame"
		elif self.header == Frame.TEST:
			return "TEST Frame"
		elif self.header == Frame.REPORT:
			return "REPORT Frame"

	def __repr__(self):
		return self.__str__()

	class Test:
		
		def __init__(self, name, scenario):
			self.name = name
			self.scenario = scenario

		def __str__(self):
			return self.name

		def __repr__(self):
			return self.__str__()

	class Report:

		PARSE, EXECUTE = range(2)
		
		def __init__(self, action, success, log, test_name=None):
			self.action = action
			self.success = success
			self.test_name = test_name
			self.log = log

		def __str__(self):
			if self.action == Report.PARSE:
				return "PARSE Report"
			elif self.action == Report.EXECUTE:
				return "EXECUTE Report"

		def __repr__(self):
			return self.__str__()
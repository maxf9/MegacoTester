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
		elif self. header == Frame.REPORT:
			return "REPORT Frame"

	def __repr__(self):
		return self.__str__()

	class Test:
		
		def __init__(self, scenario):
			self.scenario = scenario

	class Report:
		
		def __init__(self):
			pass
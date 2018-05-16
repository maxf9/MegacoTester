class Frame:
	"""Class that defines the composition of messages exchanged between application components

	The Frame instance has two fields: header (mandatory) and payload (optional)
	The Frame instance can have one of two payload types - Test, Report - or None
	"""

	STOP, TEST, REPORT = range(3)  # Defines the types of Frame headers

	def __init__(self, header, payload=None):
		self.header = header
		self.payload = payload

	class Test:
		"""Class that defines the Test payload of Frame

		The Test instance has two mandatory fields: name and scenario
		"""
		
		def __init__(self, name, scenario):
			self.name = name
			self.scenario = scenario

	class Report:
		"""Class that defines the Report payload of Frame"""

		PARSE, EXECUTE = range(2)  # Defines the types of reported actions
		
		def __init__(self, action, success, log, test_name=None):
			self.action = action        # Reported action (PARSE or EXECUTE)
			self.success = success      # Success indicator (True or False)
			self.test_name = test_name  # Name of reported test
			self.log = log              # Log of reported test
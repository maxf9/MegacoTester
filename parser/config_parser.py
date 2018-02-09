class ConfigParser:

	_instance = None
	_file_system = None

	def __new__(cls, *args):
		if ConfigParser._instance is None:
			ConfigParser._instance = object.__new__(cls)
		return ConfigParser._instance

	def __init__(self, file_system):
		ConfigParser._file_system = file_system

	def parse_config(self, config_file):
		pass
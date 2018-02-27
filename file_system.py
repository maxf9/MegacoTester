from os.path import isfile, isdir
from os import access, R_OK, X_OK

class FileSystem:

	@staticmethod
	def dump_to(file, content):
		try:
			with open(file, "w", encoding="utf-8") as f:
				f.write(content)
		except EnvironmentError:
			pass

	@staticmethod
	def load_from(file):
		if isfile(file) and access(file, R_OK):
			with open(file, "r", encoding="utf-8") as f:
				content = f.read()
				return content

	@staticmethod
	def is_acceptable_directory(path):
		if isdir(path) and access(path, X_OK):
			return True

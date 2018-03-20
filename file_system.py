from os import access, listdir, makedirs, remove, R_OK, X_OK
from os.path import isfile, isdir

class FileSystem:
	"""Static class for working with file system"""

	@staticmethod
	def dump_to(file, content):
		"""Writes the passed content to a file"""
		with open(file, "w", encoding="utf-8") as f:
			f.write(content)

	@staticmethod
	def load_from(file, binary=True):
		"""Loads contents from file

		If binary is True it will load contents in binary mode
		Returns the contents of the file, if it exists, or None
		"""
		if isfile(file) and access(file, R_OK):
			with open(file, "br" if binary else "r") as f:
				content = f.read()
				return content

	@staticmethod
	def create_dir(path):
		"""Creates directory according to path"""
		if isdir(path):
			FileSystem._clear_dir(path)
		else:
			makedirs(path)

	@staticmethod
	def _clear_dir(path):
		"""Deletes all files from the directory according to path"""
		for file in listdir(path):
			if isfile(path + "/" + file):
				remove(path + "/" + file)

	@staticmethod
	def is_acceptable_directory(path):
		"""Checks the accessable of directory according to path

		Returns True if passed path is an accessable directory 
		"""
		if isdir(path) and access(path, X_OK):
			return True

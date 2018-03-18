from os.path import isfile, isdir
from os import access, listdir, makedirs, remove, R_OK, X_OK

class FileSystem:

	@staticmethod
	def dump_to(file, content):
		with open(file, "w", encoding="utf-8") as f:
			f.write(content)

	@staticmethod
	def load_from(file, binary=True):
		if isfile(file) and access(file, R_OK):
			with open(file, "br" if binary else "r") as f:
				content = f.read()
				return content

	@staticmethod
	def create_dir(path):
		if isdir(path):
			FileSystem._clear_dir(path)
		else:
			makedirs(path)

	@staticmethod
	def _clear_dir(path):
		for file in listdir(path):
			if isfile(path + "/" + file): remove(path + "/" + file)

	@staticmethod
	def is_acceptable_directory(path):
		if isdir(path) and access(path, X_OK):
			return True

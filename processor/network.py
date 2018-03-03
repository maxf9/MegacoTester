from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
from sys import exit

class NetworkAdapter:
	
	def __init__(self, from_node, *to_nodes):
		self._socket = NetworkAdapter._configure_socket(from_node)
		self.routes = NetworkAdapter._configure_routes(*to_nodes)
		self.buffer = from_node.network_buffer
		self.node_id = from_node.id

	@staticmethod
	def _configure_socket(node):
		try:
			sock = socket(AF_INET, SOCK_DGRAM)
			sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			sock.bind((node.ip_address,node.port))
		except (OSError,IOError) as error_info:
			print("Ошибка создания сокета для Node '{id}': {error}'".format(id=node.id, error=error_info))
			exit(1)
		return sock

	@staticmethod
	def _configure_routes(*nodes):
		return dict([(node.id, (node.ip_address,node.port)) for node in nodes]) 

	def send(self, message, to_node):
		pass

	def recv(self):
		pass

	def close(self):
		self._socket.close()

	def __str__(self):
		return "Network adapter for Node '%s'" % self.node_id

	def __repr__(self):
		return self.__str__()
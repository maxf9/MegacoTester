from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR

class NetworkAdapter:
	
	def __init__(self, from_node, *to_nodes):
		self._socket = NetworkAdapter._configure_socket(from_node)
		self.routes = NetworkAdapter._configure_routes(*to_nodes)
		self.buffer = None

	@staticmethod
	def _configure_socket(node):
		sock = socket(AF_INET,SOCK_DGRAM)
		sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		return sock

	@staticmethod
	def _configure_routes(*nodes):
		pass

	def send(self, message):
		pass

	def recv(self):
		pass

	def close(self):
		self._socket.close()

	def __str__(self):
		return "Network adapter"

	def __repr__(self):
		return self.__str__()
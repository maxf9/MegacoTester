from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR

class NetworkAdapter:
	
	def __init__(self):
		self.socket = NetworkAdapter.configure_socket()
		self.routes = None
		self.buffer = None

	@staticmethod
	def configure_socket():
		sock = socket(AF_INET,SOCK_DGRAM)
		sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		return sock

	def send(self, message):
		pass

	def recv(self):
		pass

	def close(self):
		self.socket.close()
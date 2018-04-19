from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
from socket import timeout as sock_timeout
from binascii import hexlify
from sys import exit

class NetworkAdapter:
	
	def __init__(self, from_node, *to_nodes):
		self._socket = NetworkAdapter._configure_socket(from_node)
		self._routes = NetworkAdapter._configure_routes(*to_nodes)
		self.buffer = from_node.network_buffer
		self.node_id = from_node.id

	@staticmethod
	def _configure_socket(node):
		try:
			sock = socket(AF_INET, SOCK_DGRAM)
			sock.bind((node.ip_address,node.port))
		except (OSError,IOError) as error_info:
			print("Ошибка создания сокета для Node '{id}': {error}'".format(id=node.id, error=error_info))
			exit(1)
		return sock

	@staticmethod
	def _configure_routes(*nodes):
		return dict([(node.id, (node.ip_address,node.port)) for node in nodes]) 

	def send(self, message, to_node):
		try:
			self._socket.sendto(message.encode(), self._routes[to_node])
		except (OSError,IOError) as error_info:
			return (False, "Ошибка отправки сообщения: %s\n" % str(error_info))
		return (True, "Сообщение успешно отправлено\n")

	def recv(self, from_node, timeout):
		"""Receives a message from a remote node

		Returns the action result, action log, remote node properties and received data
		"""
		self._socket.settimeout(timeout/1000)    # Setting a timeout for the receiving action
		try:
			data, node = self._socket.recvfrom(self.buffer)
		except (OSError, IOError, sock_timeout) as error:
			return (False, "Message has not received: " + str(error), None)
		else:
			if node != self._routes[from_node]:  # The message must be received from the expected node
				return (False, "Message has received from unexpeted node '%s:%s'" % node, hexlify(data).decode("ascii"))
		return (True, "Message has successfully received from node '%s:%s'" % node, data.decode())

	def close(self):
		self._socket.close()

	def __repr__(self):
		return "Network adapter for Node '%s'" % self.node_id
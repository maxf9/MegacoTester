class VariablesTreeBuilder:

	_instance = None

	def __new__(cls, *args, **kwargs):
		if VariablesTreeBuilder._instance is None:
			VariablesTreeBuilder._instance = object.__new__(cls)
		return VariablesTreeBuilder._instance

	def __init__(self, config):
		self.config = config
		self._var_tree = VariableTree()
		self._makers = self._define_makers()

	def _define_makers(self):
		return {
		    "Globals" : self._make_globals,
		    "Dialplans" : self._make_dialplans,
		    "Nodes" : self._make_nodes,
		    "name" : self._make_name,
		    "ip_address" : self._make_ip_address,
		    "port" : self._make_port,
		    "mid" : self._make_mid,
		    "encoding" : self._make_encoding,
		    "network_buffer" : self._make_network_buffer,
		    "terms" : self._make_terms
		}

	def _make_globals(self, section):
		for variable, value in section.items():
			self._var_tree.childs.append(VariableTree.TreeNode(variable, value))

	def _make_dialplans(self, section):
		dialplans = VariableTree.TreeNode("Dialplans")
		for number, value in enumerate(section):
			dialplans.childs.append(VariableTree.TreeNode(str(number), value))
		self._var_tree.childs.append(dialplans)

	def _make_nodes(self, section):
		nodes = VariableTree.TreeNode("Nodes")
		for node in section:
			nodes.childs.append(self._make_node(node))
		self._var_tree.childs.append(nodes)

	def _make_node(self, fabric):
		node = VariableTree.TreeNode(str(fabric.id))
		for parameter, value in fabric.__dict__.items():
			if parameter != "id":
				node.childs.append(self._makers[parameter](value))
		return node

	def _make_name(self, value):
		return VariableTree.TreeNode("name", value)

	def _make_ip_address(self, value):
		return VariableTree.TreeNode("ip_address", value)

	def _make_port(self, value):
		return VariableTree.TreeNode("port", str(value))

	def _make_mid(self, value):
		return VariableTree.TreeNode("mid", value)

	def _make_encoding(self, value):
		return VariableTree.TreeNode("encoding", value)

	def _make_network_buffer(self, value):
		return VariableTree.TreeNode("network_buffer", str(value))

	def _make_terms(self, fabric):
		terms = VariableTree.TreeNode("terms")
		for number, value in enumerate(fabric):
			terms.childs.append(VariableTree.TreeNode(str(number), value))
		return terms

	def build_tree(self):
		for name, section in {"Globals":self.config.globals, 
		                      "Dialplans" : self.config.dialplans, 
		                      "Nodes" : self.config.nodes}.items():
			self._makers[name](section)
		return self._var_tree

class VariableTree:
	
	def __init__(self):
		self.childs = []

	class TreeNode:

		def __init__(self, identifier, value=None):
		    self.identifier = identifier
		    self.value = value
		    self.childs = [] if value is None else None

		def __repr__(self):
			return "TreeNode: %s" % self.identifier

	def get_variable(self, path, subtree=None):
		subtree = subtree if subtree else self.childs
		segment = path[0]                  
		for child in subtree:
			if child.identifier == segment:
				if child.value is None:
					if len(path) != 1:             
						return self.get_variable(path[1:], subtree=child.childs)
				elif len(path) == 1:                
					return child.value
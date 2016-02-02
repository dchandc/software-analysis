#!/usr/bin/python

import argparse, re, sys

class node(object):
	def __init__(self, name = None, parent = None, children = []):
		self.name = name
		self.parent = parent
		self.children = children or []
		self.call_count = 1
		if parent:
			self.depth = parent.depth + 1
		else:
			self.depth = 0

	def add_child(self, child = None):
		self.children.append(child)

	def __repr__(self, level = 0): 
		ret = '\t' * level + repr(self.name) + ' (' + repr(self.depth) + ',' + repr(self.call_count) + ')\n'
        	for child in self.children:
	            	ret += child.__repr__(level + 1)
        	return ret

##########

parser = argparse.ArgumentParser()
parser.add_argument('call_file', type=argparse.FileType('r'), help='file containing method calls')
args = parser.parse_args()

root_node = node('method_call_root')
current_node = root_node

for line in args.call_file:
	m = re.match(r'\[call\] (\S+)', line)
	if m:
		method_name = m.group(1)
		child_node = None
		for child in current_node.children:
			if child.name == method_name:
				child.call_count += 1
				child_node = child
				break
		if not child_node:
			child_node = node(method_name, current_node)
			current_node.add_child(child_node)
		current_node = child_node
	else:
		m = re.match(r'\[return\] (\S+)', line)
		if m:
			method_name = m.group(1)
			if method_name != current_node.name:
				sys.exit('invalid return: ' + line)
			if not current_node.parent:
				sys.exit('missing parent: ' + line)
			current_node = current_node.parent
		else:
			sys.exit('unknown line: ' + line)

print root_node
if current_node != root_node:
	print 'failed to return root'

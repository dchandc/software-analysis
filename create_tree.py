#!/usr/bin/python

import argparse, re

class node(object):
	def __init__(self, name = None, parent = None, children = []):
		self.name = name
		self.parent = parent
		self.children = children or []

	def __repr__(self, level = 0): 
		ret = "\t"*level+repr(self.name)+"\n"
        	for child in self.children:
	            	ret += child.__repr__(level + 1)
        	return ret

	def add_child(self, child = None):
		self.children.append(child)

parser = argparse.ArgumentParser()
parser.add_argument('call_file', type=argparse.FileType('r'), help='file containing method calls')
args = parser.parse_args()

root_node = node('__root__')
current_node = root_node

num_returns = 0
for line in args.call_file:
	m = re.match(r'\[call\] (\S+)', line)
	if m:
		method_name = m.group(1)
		child_node = node(m.group(1), current_node)
		current_node.add_child(child_node)
		current_node = child_node
		continue
	m = re.match(r'\[return\] (\S+)', line)
	if m:
		method_name = m.group(1)
		if method_name != current_node.name:
			sys.exit('invalid return: ' + line)
		if not current_node.parent:
			sys.exit('missing parent: ' + line)
		current_node = current_node.parent
		num_returns += 1

print root_node
if current_node != root_node:
	print 'failed to return root'

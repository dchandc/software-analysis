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

	def call_child(self, method_name = None):
		child_node = None
		for child in self.children:
			if child.name == method_name:
				child.call_count += 1
				child_node = child
				break
		if not child_node:
			child_node = node(method_name, self)
			self.children.append(child_node)
		return child_node

	def return_call(self, method_name = None):
		if method_name != self.name:
			sys.exit(self.name + ': invalid return')
		if not self.parent:
			sys.exit(self.name + ': missing parent')
		return self.parent

	def __repr__(self, level = 0): 
		ret = '\t' * level + repr(self.name) + ' (' + repr(self.depth) + ',' + repr(self.call_count) + ')\n'
        	for child in self.children:
	            	ret += child.__repr__(level + 1)
        	return ret

##########

parser = argparse.ArgumentParser()
parser.add_argument('call_file', type=argparse.FileType('r'), help='file containing method calls')
parser.add_argument('-k', type=int, metavar='LENGTH', choices=range(1, 10), default=1, help='length of call sequences')
parser.add_argument('--no-returns', action='store_true')
args = parser.parse_args()

root_node = node('method_call_root')
current_node = root_node

method_counts = {}
sequence_counts = {}
current_sequence = []

for line in args.call_file:
	m = re.match(r'\[Call\] (\S+)', line)
	if m:
		method_name = m.group(1)
		current_node = current_node.call_child(method_name)

		if method_name not in method_counts:
			method_counts[method_name] = 1
		else:
			method_counts[method_name] += 1

		current_sequence.append('>' + method_name)
		if len(current_sequence) >= args.k:
			sequence_str = ', '.join(current_sequence)
			if sequence_str not in sequence_counts:
				sequence_counts[sequence_str] = 1
			else:
				sequence_counts[sequence_str] += 1
			current_sequence.pop(0)
	else:
		m = re.match(r'\[Return\] (\S+)', line)
		if m:
			method_name = m.group(1)
			current_node = current_node.return_call(method_name)

			if not args.no_returns:
				current_sequence.append('<' + method_name)
				if len(current_sequence) >= args.k:
					sequence_str = ', '.join(current_sequence)
					if sequence_str not in sequence_counts:
						sequence_counts[sequence_str] = 1
					else:
						sequence_counts[sequence_str] += 1
					current_sequence.pop(0)

print root_node
if current_node != root_node:
	print 'failed to return root'
print method_counts
print sequence_counts

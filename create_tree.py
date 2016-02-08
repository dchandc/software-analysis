#!/usr/bin/python

import argparse, re, sys

children_counts = {}
depth_counts = {}

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
		children_counts[name] = 0

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
			if self.name not in children_counts:
				children_counts[self.name] = 1
			else:
				children_counts[self.name] += 1
		return child_node

	def return_call(self, method_name = None):
		if not self.parent:
			sys.exit(self.name + ': missing parent')
		if str(self.depth) not in depth_counts:
			depth_counts[str(self.depth)] = 1
		else:
			depth_counts[str(self.depth)] += 1
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
owner_counts = {}
current_sequence = []
line_index = 0

for line in args.call_file:
	line_index += 1
	m = line.split()
	if len(m) == 2:
		method_type = m[0]
		method_name = m[1]
		if method_type == "[Call]":
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

			method_name_split = method_name.split('::')
			owner_name = method_name_split[0]	
			if owner_name not in owner_counts:
				owner_counts[owner_name] = 1
			else:
				owner_counts[owner_name] += 1
		elif method_type == "[Return]":
			if method_name != current_node.name:
				if method_name == current_node.parent:
					current_node = current_node.parent.return_call(method_name)
			else:
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

#print method_counts
#print sequence_counts
#print owner_counts
#print children_counts
#print depth_counts

#with open('method_counts.csv', 'w') as f:
#	f.write('method_name,count\n')
#	for sorted_key in sorted(method_counts, key=method_counts.get, reverse=True):
#		f.write(sorted_key + ',' + str(method_counts[sorted_key]) + '\n')
#
#sequence_file = 'sequence' + str(args.k) + '_counts'
#if not args.no_returns:
#	sequence_file += '_returns'
#sequence_file += '.csv'
#with open(sequence_file, 'w') as f:
#	f.write('sequence_str,count\n')
#	for sorted_key in sorted(sequence_counts, key=sequence_counts.get, reverse=True):
#		f.write(sorted_key + ',' + str(sequence_counts[sorted_key]) + '\n')
#
#with open('owner_counts.csv', 'w') as f:
#	f.write('owner_name,count\n')
#	for sorted_key in sorted(owner_counts, key=owner_counts.get, reverse=True):
#		f.write(sorted_key + ',' + str(owner_counts[sorted_key]) + '\n')
#
#with open('children_counts.csv', 'w') as f:
#	f.write('method_name,count\n')
#	for sorted_key in sorted(children_counts, key=children_counts.get, reverse=True):
#		f.write(sorted_key + ',' + str(children_counts[sorted_key]) + '\n')

with open('depth_counts.csv', 'w') as f:
	f.write('depth,count\n')
	for key in sorted(depth_counts.iterkeys(), cmp=lambda x, y: cmp(int(x), int(y))):
		f.write(key + ',' + str(depth_counts[key]) + '\n')

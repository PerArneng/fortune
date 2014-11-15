#!/usr/bin/env python

import re
import sys
import os
import sets

def is_file(file):
	if file is None:
		return false
	return os.path.isfile(file)

def extract_path(pattern, line, group_nr):
	match = pattern.search(line)
	path = None
	if match:
		file = match.group(group_nr)
		if is_file(file):
			path = file	
	return path


def main():

	if len(sys.argv) < 2:
		print "usage: filefilter <(strace|ldd) output...>"
		exit(1)
	
	strace_pattern = re.compile('(open|stat|execve)\("([^"]+)"')
	ldd_pattern = re.compile('(/.*) \(0x\w+\)$')

	for arg_file in sys.argv[1:]:

		output_file = open(arg_file, "r")

		path_set = sets.Set()

		for line in output_file:

			path = extract_path(strace_pattern, line, 2)
			if path is not None:
				path_set.add(path)

			path = extract_path(ldd_pattern, line, 1)
			if path is not None:
				path_set.add(path)

		for path in path_set:
			print path


if __name__ == "__main__":
	main()


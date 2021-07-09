"""
usage:
	python simple_display.py <filename> [-a] [-d=<depth>] [-p=<path>] [-m=<map_path>]

 - `-h` : print this help message and exit (can be anywhere)
 - `filename` : hdf5 file to open
 - `-a`	: if flag passed, print attributes as well
 - `-d` : argument is maximum depth. defaults to 64
 - `-p` : argument is specific path within the file
 - `-m` : argument is path (in hdf5 file) of group whose 
            attributes map types to shorted typenames

first prints datatype legend (if -m specified), surrounded by '=' hrules

then prints table with columns:
 - 'path'  : path of object inside hdf5 file
 - 'etype' : the element type (usually a group, dataset, or attribute)
               note that attributes are printed below their parent group
 - 'dtype' : datatype, if element is a dataset or attribute
 - 'info'  : random info, depends on the element type
	- s : shape (Datasets)
	- c : number of first order children (Groups)
	- a : number of attributes (Groups)
	- v : element value (attribute)


"""

import sys
import numpy as np

import h5py

if __name__ == 'hdf5_tools.h5view':
	from hdf5_tools.hdf5_tools import info_members_recursive,load_dataset,ElementInfo,DataSetPath,TYPENAMES,print_info
else:
	from hdf5_tools import info_members_recursive,load_dataset,ElementInfo,DataSetPath,TYPENAMES,print_info

def read_cmd(argv):
	"""
	splits a list of strings `'--flag=val'` with combined flags and args
	into a dict: `{'flag' : 'val'}` (lstrips the dashes)

	if flag `' flag '` passed without value returns for that flag: `{'flag' : True}`
	"""	
	output = {}
	for x in argv:
		x = x.lstrip('-')
		pair = x.split('=',1)
		if len(pair) < 2:
			pair = pair + [True]

		output[pair[0]] = pair[1]

	return output

def main(argv = sys.argv):
	# check args
	if (len(argv) < 2):
		raise Exception(f'improper number of arguments.\n\n\n{__doc__}\n\n')
	
	# filename always first arg
	filename = argv[1]
	
	# parse the rest
	args = read_cmd(argv[2:])

	if ('h' in args) or (filename.strip('-') in ['h', 'help']):
		print(__doc__)
		exit(0)
	
	# check for flags
	print_attr = False
	if 'a' in args:
		print_attr = True
	
	# depth flag
	depth = 64
	if 'd' in args:
		depth = int(args['d'])
	
	# path flag
	path = None
	if 'p' in args:
		path = args['p'].strip('"').strip("'")

	# dtype map flag
	map_dtypes_path = None
	if 'm' in args:
		map_dtypes_path = args['m'].strip('"').strip("'")

	# open the file and print the table
	with h5py.File(filename, 'r') as root:
		print_info(
			group = root,
			path = path,
			depth = depth,
			print_attr = print_attr,
			map_dtypes_path = map_dtypes_path,
		)

	
if __name__ == "__main__":
	main(sys.argv)

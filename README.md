# `hdf5_tools`
provides some wrapper functions for the [`h5py` library](https://www.h5py.org)


## `h5view.py`
`h5view.py` allows the listing of the groups, attributes, and datasets in a `.hdf5` file without having to open the GUI. Also allows for the printing of datasets as numpy arrays.
do `python h5view.py -h` for help

### Usage:
```bash
	python simple_display.py <filename> [-a] [-d=<depth>] [-p=<path>] [-m=<map_path>]
```

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


### Examples:
```bash
$ h5view data_example.h5
--------------------------------------------------------------------------------
 path         : etype       dtype           info
--------------------------------------------------------------------------------
 .            : File                        c=3, a=2
 labels       : Dataset     int32           s=(10,)
 labels_map   : Group                       c=0, a=1
 spectrograms : Dataset     float32         s=(10, 1000, 65)
```

```bash
$ h5view data_example.h5 -a
--------------------------------------------------------------------------------
 path             : etype       dtype           info
--------------------------------------------------------------------------------
 .                : File                        c=3, a=2
     dataset_name : attr        str             v=testing
     n_samples    : attr        int32           v=10
 labels           : Dataset     int32           s=(10,)
 labels_map       : Group                       c=0, a=1
     right        : attr        int32           v=0
 spectrograms     : Dataset     float32         s=(10, 1000, 65)
```


# future plans:
integration with:
 - https://github.com/CINPLA/exdir
 - https://github.com/CINPLA/hdf5-exdir-converter
"""
2020-09
"""

# standard library packages
import os
from h5py._hl.files import File
from h5py._hl.group import Group
import numpy as np
from typing import *
from collections import namedtuple 

import h5py

# object storing where to find a dataset
DataSetPath = namedtuple('DataSetPath', ['filename', 'hdf5_path'])

def read_cmd(argv : List[str]) -> Dict[str,str]:
    """command line arg reader utility

    splits a list of strings `'--foo=bar'` with combined flags and args
    into a dict: `{'flag' : 'bar'}` (lstrips the dashes)

    if flag `'foo'` passed without value returns for that flag: `{'foo' : True}`

    Args:
        argv (List[str]): expected to be sys.argv

    Returns:
        Dict[str,str]
    """

    output = {}
    for x in argv:
        x = x.lstrip('-')
        pair = x.split('=',1)
        if len(pair) < 2:
            pair = pair + [True]

        output[pair[0]] = pair[1]
    return output


blankstr = ' '



def is_Group(myobj) -> bool:
    return isinstance(myobj, h5py.Group)

def is_Datatype(myobj) -> bool:
    return isinstance(myobj, h5py.Datatype)

def is_Dataset(myobj) -> bool:
    return isinstance(myobj, h5py.Dataset)

def get_group_shape(grp : h5py.Group) -> str:
    return 'c=%i, a=%i' % (
        len(grp.keys()),
        len(grp.attrs.keys()),
    )

def get_shape_general(myobj : Any) -> str:
    if is_Dataset(myobj) or isinstance(myobj, np.ndarray):
        return 's='+str(myobj.shape)
    elif is_Group(myobj):
        return get_group_shape(myobj)
    elif hasattr(myobj, 'shape'):
        return str(myobj.shape)
    else:
        return blankstr

ElementInfo = namedtuple('ElementInfo', ['path', 'etype', 'dtype', 'shape'])
TYPENAMES = {
    h5py.Dataset : 'Dataset',
    h5py.Datatype : 'Datatype',
    h5py.File : 'File',
    h5py.Group : 'Group',
}

def info_members_recursive(root_group : h5py.Group, with_groups = False, depth = 1024) -> List[ElementInfo]:
    """list all members of a dictionary, with some metadata

    Args:
        root_group (h5py.Group): root group from which tree traversal starts and paths given relative to

    Returns:
        List[ElementInfo]: list of every path in the hdf5 file and some metadata
    """
    output = []

    for k in root_group:
        if is_Group(root_group[k]) and (depth > 1):
            temp = info_members_recursive(
                with_groups = True,
                root_group = root_group[k],
                depth = depth - 1,
            )
            if with_groups:
                temp_new = [ElementInfo(
                    path = k,
                    etype = 'Group',
                    dtype = blankstr,
                    shape = get_shape_general(root_group[k]),
                )]
            else:
                temp_new = []
            for x in temp:
                temp_new.append(ElementInfo(
                    path = k + '/' + x.path,
                    etype = x.etype,
                    dtype = x.dtype,
                    shape = get_shape_general(x.shape),
                ))
                
            output = output + temp_new
    
        else:
            output.append(ElementInfo(
                path = k,
                etype = TYPENAMES[type(root_group[k])] if type(root_group[k]) in TYPENAMES else str(type(root_group[k])),
                dtype = str(root_group[k].dtype) if is_Dataset(root_group[k]) else blankstr,
                shape = get_shape_general(root_group[k]),
            ))

    return output
    

def list_members_recursive(root_group : h5py.Group) -> List[str]:
    """list all members of a dictionary

    Args:
        root_group (h5py.Group): root group from which tree traversal starts and paths given relative to

    Returns:
        List[str]: list of every path in the hdf5 file
    """
    output = []
    for k in root_group:
        if is_Group(root_group[k]):
            output = output + [
                k + '/' + x
                for x in list_members_recursive(root_group[k])
            ]
        else:
            output.append(k)

    return output

def list_members_recursive_tablesOnly(root_group : h5py.Group) -> List[str]:
    """same as list_members_recursive() but excludes everything that isnt a Dataset"""
    output = [
        g for g in list_members_recursive(root_group)
        if is_Dataset(g)
    ]
    return output
    
    

def load_dataset(data_path : DataSetPath) -> np.ndarray:
    """[summary]

    [extended_summary]

    Args:
        data_path (DataSetPath): [description]

    Raises:
        FileNotFoundError: [description]
        TypeError: [description]
        KeyError: [description]

    Returns:
        np.ndarray: [description]
    """
    # unpack data_path
    filename, hdf5_path = data_path
    
    # context manager opens file in read-only mode ('r') and closes at end of block
    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)
    
    with h5py.File(filename, 'r') as fin:
        print('> loading file:\t%s' % filename)
        
        # check key exists and is of valid type
        if hdf5_path in fin:
            data = fin[hdf5_path]
            if isinstance(data, h5py.Dataset):
                print('> \tfound dataset:\t%s' % hdf5_path)
            else:
                raise TypeError(
                    '`%s` is not a valid dataset, is of type %s' 
                    % (hdf5_path, type(data))
                )
        else:
            raise KeyError('could not find anything with key:\t%s' % hdf5_path)
        
        print('> \tconverting to numpy array')
        
        return np.array(data)


# make format strings
# FMT_row = '{:<29} : ' + '{:<8}' + '{:<16}' + '{:<16}'
# FMT_attr = '    {:<25} : ' + 'attr    ' + '{:<16}' + '{}' 

FMT_row_suf = ': ' + '{:<12}' + '{:<16}' + '{:<16}'

# nonestr = lambda x : str(x)
# nonestr = lambda x : ' ' if ((x is None) or (x == 'None' if isinstance(x,str) else True)) else str(x)


def print_info(
        group : h5py.Group,
        path : Optional[str] = None,
        depth : int = 64,
        print_groups : bool = True,
        print_attr : bool = False, 
        output : Optional[File] = None,
        map_dtypes_path : Optional[str] = None,
    ):

    # if a path is given, go to that path
    if path is not None:
        data = group[path]
    else:
        data = group
    
    # if that is a dataset, print it
    if is_Dataset(data):
        if print_attr:
            for a_key,a_val in data.attrs.items():
                print('{:<20}'.format(a_key) + FMT_row_suf.format('attr    ', a_val.__class__.__name__, a_val))
            print('-'*30)
            print('shape = %s' % str(data.shape))
            print('dtype = %s' % str(data.dtype))
            print('='*30)

        print(np.array(data))
        return

    # get all relevant rows
    # first item is root, added in manually
    info = [ElementInfo(
        path = '.',
        etype = TYPENAMES[type(data)] if type(data) in TYPENAMES else str(type(data)),
        dtype = blankstr,
        shape = get_shape_general(data),
    )] + info_members_recursive(
        root_group = data,
        with_groups = print_groups,
        depth = depth,
    )
    
    # adjust table size
    max_path_size = 1 + max(len(x.path) for x in info)
    if print_attr:
        attr_path_lengths = []
        for x in info:
            if x.etype in ['Dataset', 'Group']:
                for a in data[x.path].attrs
                    attr_path_lengths.append(len(a))

        if not attr_path_lengths:
            attr_path_lengths = [0]
        max_path_size = max(
            max_path_size,
            5 + max(attr_path_lengths)
        )
    
    FMT_row = ' {:<' + str(max_path_size) + '}' + FMT_row_suf

    # map dtypes
    if map_dtypes_path is not None:
        # read the map from the hdf5 file
        if map_dtypes_path in data:
            map_dtypes = read_map_dtypes(data, map_dtypes_path)
        else:
            raise KeyError('invalid path for dtype map:   -m=%s' % map_dtypes_path)
        
        print('datatype legend:')
        print('='*50 + '\n')
        for key,val in map_dtypes.items():
            print('    {:<20} : {}\n'.format(val,key))
        print('='*50)

        # for each element, map the datatype
        info = [
            ElementInfo(
                path = elmt.path,
                etype = elmt.etype,
                dtype = map_dtypes[str(elmt.dtype)] if str(elmt.dtype) in map_dtypes else str(elmt.dtype),
                shape = elmt.shape
            )
            for elmt in info
            if elmt.path != map_dtypes_path # exclude the map we used
        ]

    
    # print table header
    print('-' * 20 * len(ElementInfo._fields))

    temp_header = list(ElementInfo._fields)
    temp_header[-1] = 'info'
    print(FMT_row.format(*temp_header))

    print('-' * 20 * len(ElementInfo._fields))

    # print every row
    for row in info:
        # print(*row)
        # print row info
        print(FMT_row.format(*(str(x) for x in row)))
        # print attributes, if requested
        if print_attr and (row.etype in ['Dataset', 'Group']):
            for a_key,a_val in data[row.path].attrs.items():
                print(FMT_row.format('    ' + a_key, 'attr    ', a_val.__class__.__name__, 'v=' + str(a_val)))



def nested_dict_to_attrs(grp : h5py.Group, data : dict):
    import dictmagic
    grp.attrs.update(dictmagic.flatten(data))

def get_pathdict_attrs(grp : h5py.Group):
    import dictmagic
    return dictmagic.unflatten(dict(grp.attrs))



def read_map_dtypes(
        root_group : h5py.Group,
        dtype_map_path : str,
    ) -> Dict[str,str]:
    """shorten dtypes by reading a map

    given a path `dtype_map_path` to some group,
    look in the attributes of that group for a map
        `shortened_typename : long_typename`
    return that map, with key value pairs reversed

    (this feature is very niche)

    Args:
        root_group (h5py.Group): group relative to which the path is
        dtype_map_path (str): path to group in whose attributes the map is

    Returns:
        Dict[str,str]: map of long typenames to shortened ones
    """
    
    base_dict = dict(root_group[dtype_map_path].attrs)
    
    return {
        v : k
        for k,v in base_dict.items()
    }
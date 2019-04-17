
import numpy as np
import ctypes as ct
import os

#Define where the library is and load it
_path = os.path.dirname('__file__')
libpygio = ct.CDLL(os.path.abspath('dtk/lib/libpygio.so'))
#we need to define the return type ("restype") and
#the argument types
libpygio.get_elem_num.restype=ct.c_int64
libpygio.get_elem_num.argtypes=[ct.c_char_p, ct.c_int]

libpygio.get_block_num.restype=ct.c_int64
libpygio.get_block_num.argtypes=[ct.c_char_p]

libpygio.get_variable_type.restype=ct.c_int
libpygio.get_variable_type.argtypes=[ct.c_char_p,ct.c_char_p]

# int 8
libpygio.read_gio_int8.restype=None
libpygio.read_gio_int8.argtypes=[ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_int8),ct.c_int]

# int 32
libpygio.read_gio_int32.restype=None
libpygio.read_gio_int32.argtypes=[ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_int),ct.c_int]

# int 64
libpygio.read_gio_int64.restype=None
libpygio.read_gio_int64.argtypes=[ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_int64),ct.c_int]

# uint 8
libpygio.read_gio_uint8.restype=None
libpygio.read_gio_uint8.argtypes=[ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_uint8),ct.c_int]


# float 
libpygio.read_gio_float.restype=None
libpygio.read_gio_float.argtypes=[ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_float),ct.c_int]

# double 
libpygio.read_gio_double.restype=None
libpygio.read_gio_double.argtypes=[ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_double),ct.c_int]

libpygio.inspect_gio.restype=None
libpygio.inspect_gio.argtypes=[ct.c_char_p]

def gio_read(file_name,var_name,block=-1):
    var_size = libpygio.get_elem_num(file_name.encode('utf-8'), block)
    var_type = libpygio.get_variable_type(file_name.encode('utf-8'),var_name.encode('utf-8'))
    if(var_type==10):
        print("Variable not found")
        raise KeyError()
    elif(var_type==9):
        print("variable type not supported (only int8/int32/int64/float/double are supported)")
        raise ValueError()
    elif(var_type==0):
        #float
        result = np.ndarray(var_size,dtype=np.float32)
        libpygio.read_gio_float(file_name.encode('utf-8'),var_name.encode('utf-8'),result.ctypes.data_as(ct.POINTER(ct.c_float)),block)
        return result
    elif(var_type==1):
        #double
        result = np.ndarray(var_size,dtype=np.float64)
        libpygio.read_gio_double(file_name.encode('utf-8'),var_name.encode('utf-8'),result.ctypes.data_as(ct.POINTER(ct.c_double)),block)
        return result
    elif(var_type==2):
        #int32
        result = np.ndarray(var_size,dtype=np.int32)
        libpygio.read_gio_int32(file_name.encode('utf-8'),var_name.encode('utf-8'),result.ctypes.data_as(ct.POINTER(ct.c_int32)),block)
        return result
    elif(var_type==3):
        #int64
        result = np.ndarray(var_size,dtype=np.int64)
        libpygio.read_gio_int64(file_name.encode('utf-8'),var_name.encode('utf-8'),result.ctypes.data_as(ct.POINTER(ct.c_int64)),block)
        return result        
    elif(var_type==4):
        #int8
        result = np.ndarray(var_size,dtype=np.int8)
        libpygio.read_gio_int8(file_name.encode('utf-8'),var_name.encode('utf-8'),result.ctypes.data_as(ct.POINTER(ct.c_int8)),block)
        return result        
    elif(var_type==5):
        #int8
        result = np.ndarray(var_size,dtype=np.uint8)
        libpygio.read_gio_uint8(file_name.encode('utf-8'),var_name.encode('utf-8'),result.ctypes.data_as(ct.POINTER(ct.c_uint8)),block)
        return result        
    else:
        raise ValueError("var_type not support {} [number to type listed in gio.hpp]".format(var_type))

def gio_inspect(file_name):
    libpygio.inspect_gio(file_name.encode('utf-8'))

def gio_get_size(file_name, block=-1):
    return libpygio.get_elem_num(file_name.encode('utf-8'), block)

def gio_get_block_num(file_name):
    return libpygio.get_block_num(file_name.encode('utf-8'))

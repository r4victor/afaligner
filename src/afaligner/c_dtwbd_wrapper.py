import ctypes
import os.path

import numpy as np


class FastDTWBDError(Exception):
    pass


BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def c_FastDTWBD(s, t, skip_penalty, radius):
    """
    Wrapper for FastDTWDB C implementation.
    """
    c_module = ctypes.cdll[os.path.join(BASE_DIR, 'c_modules/dtwbd.so')]
    c_module.FastDTWBD.argtypes = (
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_size_t),
    )
    c_module.FastDTWBD.restype = ctypes.c_ssize_t
    
    n, l = s.shape
    m, _ = t.shape
    path_distance = ctypes.c_double()
    path_buffer = np.empty((n+m, 2), dtype='uintp')
    path_len = c_module.FastDTWBD(
        s.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        t.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_size_t(n),
        ctypes.c_size_t(m),
        ctypes.c_size_t(l),
        ctypes.c_double(skip_penalty),
        radius,
        ctypes.byref(path_distance),
        path_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_size_t))
    )

    if path_len < 0:
        raise FastDTWBDError(
            'The FastDTWDB() C function raised an error. '
            'See stderr for more details.'
        )

    return path_distance.value, path_buffer[:path_len]
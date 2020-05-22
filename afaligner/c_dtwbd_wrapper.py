import ctypes
import os.path

import numpy as np


BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def c_FastDTWBD(s, t, skip_penalty, radius):
    """
    Wrapper for FastDTWDB C implementation.
    """
    c_module = ctypes.cdll[os.path.join(BASE_DIR, 'c_modules/dtwbd.so')]
    n, l = s.shape
    m, _ = t.shape
    path_distance = ctypes.c_double()
    path_buffer = np.empty((n+m, 2), dtype='int64')
    path_len = c_module.FastDTWBD(
        s.ctypes,
        t.ctypes,
        ctypes.c_size_t(n),
        ctypes.c_size_t(m),
        ctypes.c_size_t(l),
        radius,
        ctypes.c_double(skip_penalty),
        ctypes.byref(path_distance),
        path_buffer.ctypes
    )
    return path_distance.value, path_buffer[:path_len]
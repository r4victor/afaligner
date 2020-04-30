from collections import defaultdict
import ctypes

import numpy as np


def DTWBD(s, t, skip_penalty, window=None):
    """
    This is a DTWDB (dynamic time warping with boundaries detection) algorithm,
    a variation of a classic DTW algorithm that
    chooses the best possible start and the end of the warping path.
    In contrast, DTW always matches the entire sequences.
    The algorithm is able to skip the first and the last few frames of both sequences
    with the cost of `skip_penalty` for each skipped frame.
    """
    # weights for diagonal, horizontal and vertical matching
    dw, hw, vw = 1,1,1

    n = len(s)
    m = len(t)

    if window is None:
        window = [(i, j) for j in range(0, m) for i in range(0, n)]

    # (distance, prev_i, prev_j, match)
    D = defaultdict(lambda: (float('inf'), None, None))
    min_path_dist = skip_penalty * (n + m)
    path_end = None

    for i, j in window:
        d = euclid_dist(s[i], t[j])
        D[i, j] = min(
            (D[i-1, j-1][0] + dw*d, i-1, j-1),
            (D[i, j-1][0] + vw*d, i, j-1),
            (D[i-1, j][0] + hw*d, i-1, j),
            (skip_penalty * (i + j) + d, None, None),
            key=lambda x: x[0]
        )

        path_dist = D[i, j][0] + skip_penalty * (n - i + m - j - 2)
        if path_dist < min_path_dist:
            min_path_dist = path_dist
            path_end = i, j

    if path_end is None:
        return min_path_dist, np.array([])

    i, j = path_end
    path = []

    while i is not None and j is not None:
        path += [(i, j)]
        i, j = D[i, j][1], D[i, j][2]

    return min_path_dist, np.array(path)[::-1]


def euclid_dist(x, y):
    return np.linalg.norm(x-y)


def c_DTWBD(s, t, skip_penalty, window=None):
    """
    Wrapper for DTWDB C implementation.
    """
    c_module = ctypes.cdll['c_modules/alignment_algorithms.so']
    n, l = s.shape
    m, _ = t.shape
    path_distance = ctypes.c_double()
    path_buffer = np.empty((n+m, 2), dtype='int32')
    path_len = c_module.DTWBD(
        s.ctypes,
        t.ctypes,
        n, m, l,
        ctypes.c_double(skip_penalty),
        ctypes.byref(path_distance),
        path_buffer.ctypes
    )
    return path_distance.value, path_buffer[:path_len]
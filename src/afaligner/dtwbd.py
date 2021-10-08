from collections import defaultdict

import numpy as np


# This file contains implementation of DTWBD and FastDTWBD algorithms in Python.
# They are not used in the project and serve only as a reference.
# C implementation, which is actually actually used, can be found in `c_modules/dtwdb.c`.


def DTWBD(s, t, skip_penalty, window=None):
    """
    This is a DTWDB (dynamic time warping with boundaries detection) algorithm,
    a variation of a classic DTW algorithm, that
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
        window = [[0, m] for i in range(n)]

    # (distance, prev_i, prev_j, match)
    D = defaultdict(lambda: (float('inf'), None, None))
    min_path_dist = skip_penalty * (n + m)
    path_end = None

    for i in range(n):
        for j in range(window[i][0], window[i][1]):
            d = _euclid_dist(s[i], t[j])
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


def _euclid_dist(x, y):
    return np.linalg.norm(x-y)


def FastDTWBD(s, t, skip_penalty, radius=0):
    min_seq_len = 2 * (radius + 2)

    if len(s) < min_seq_len or len(t) < min_seq_len:
        return DTWBD(s, t, skip_penalty)
    
    coarsed_s = _coarse_seq(s)
    coarsed_t = _coarse_seq(t)

    _, path = FastDTWBD(coarsed_s, coarsed_t, skip_penalty, radius)
    window = _get_window(path, radius, len(s), len(t))

    return DTWBD(s, t, skip_penalty, window)


def _coarse_seq(seq):
    even = seq[::2, :]
    odd = seq[1::2, :]
    l = len(seq) // 2
    return (even[:l] + odd[:l]) / 2


def _get_window(path, radius, n, m):
    window = np.array([[m, 0] for _ in range(n)], dtype='uint64')

    if len(path) == 0:
        return window

    for i, j in path:
        for x in range(-radius, radius+1):
            for y in [-radius, radius+1]:
                for cell_i, cell_j in _project_cell(i+x, j+y):
                    _update_window(window, n, m, cell_i, cell_j)

    return window


def _project_cell(i, j):
    return [(2*i, 2*j), (2*i, 2*j+1), (2*i+1, 2*j), (2*i+1, 2*j+1)]


def _update_window(window, n, m, i, j):
    if i < 0 or i >= n:
        return

    j = min(j, m-1)
    j = max(j, 0)

    if j < window[i][0]:
        window[i][0] = j
    if j >= window[i][1]:
        window[i][1] = j + 1
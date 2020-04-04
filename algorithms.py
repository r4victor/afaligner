from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt


# Синхронизация аудио и текста.
# Выравнивание последовательностей с учетом трансформации временной шкалы и структурных различий


def simpleDTW(s, t, dist, window=None):
    n = len(s)
    m = len(t)
    D = [[None]*m for _ in range(n)]

    D[0][0] = dist(s[0], t[0]), None, None

    for j in range(1, m):
        D[0][j] = D[0][j-1][0] + dist(s[0], t[j]), 0, j-1
    for i in range(1, n):
        D[i][0] = D[i-1][0][0] + dist(s[i], t[0]), i-1, 0

    for i in range(1, n):
        for j in range(1, m):
            d = dist(s[i], t[j])
            D[i][j] = min(
                (d+D[i-1][j][0], i-1, j),
                (d+D[i-1][j-1][0], i-1, j-1),
                (d+D[i][j-1][0], i, j-1),
                key=lambda x: x[0]
            )

    i, j = n-1, m-1
    distance = D[i][j][0]
    path = []

    while True:
        path += [(i, j)]
        i, j = D[i][j][1], D[i][j][2]
        if i is None or j is None:
            return distance, list(reversed(path))


def DTW(s, t, dist, window=None):
    n = len(s)
    m = len(t)

    if window is None:
        window = [(i, j) for j in range(0, m) for i in range(0, n)]

    D = defaultdict(lambda: (float('inf'), None, None))
    D[0, 0] = (0, None, None)

    for i, j in window[1:]:
        d = dist(s[i], t[j])
        D[i, j] = min(
            (d+D[i-1, j-1][0], i-1, j-1),
            (d+D[i-1, j][0], i-1, j),
            (d+D[i, j-1][0], i, j-1),
            key=lambda x: x[0]
        )

    i, j = n-1, m-1
    distance = D[i, j][0]
    path = []

    while True:
        path += [(i, j)]
        i, j = D[i, j][1], D[i, j][2]
        if i is None or j is None:
            return distance, list(reversed(path)), D


def FastDTW(s, t, dist, radius=0):
    min_seq_len = radius + 2

    if len(s) < min_seq_len or len(t) < min_seq_len:
        return DTW(s, t, dist)
    
    coarsed_s = coarse_seq(s)
    coarsed_t = coarse_seq(t)

    _, path, _ = FastDTW(coarsed_s, coarsed_t, dist, radius)
    window = get_window(path, radius, len(s), len(t))

    return DTW(s, t, dist, window)


def coarse_seq(seq):
    even = seq[::2, :]
    odd = seq[1::2, :]
    l = len(seq) // 2
    return (even[:l] + odd[:l]) / 2


def get_window(path, radius, s_len, t_len):
    window_cells = set()
    path_to_project = path + [(path[-1][0] + s_len % 2, path[-1][1] + t_len % 2)]

    for i, j in path_to_project:
        for x in range(-radius, radius+1):
            for y in range(-radius, radius+1):
                window_cells.update(project_cell(i+x, j+y))
        
        # project continuously

    # return sorted(window_cells)

    # order window's cells in columns
    window = []
    j_start = 0
    for i in range(0, s_len):
        next_j_start = None
        for j in range(j_start, t_len):
            if (i, j) in window_cells:
                window.append((i, j))
                if next_j_start is None:
                    next_j_start = j
            elif next_j_start is not None:
                break
        j_start = next_j_start

    return window


def project_cell(i, j):
    return [(2*i, 2*j), (2*i, 2*j+1), (2*i+1, 2*j), (2*i+1, 2*j+1)]


def discard_cells_outside_matrix(cells, s_len, t_len):
    return [(i, j) for i, j in cells if 0 <= i < s_len and 0 <= j < t_len]


def NW(s, t, dist, gap_penalty):
    n = len(s)
    m = len(t)
    D = [[None]*(m+1) for _ in range(n+1)]

    D[0][0] = 0
    for j in range(1, m+1):
        D[0][j] = D[0][j-1] + gap_penalty
    for i in range(1, n+1):
        D[i][0] = D[i-1][0] + gap_penalty

    for i in range(1, n+1):
        for j in range(1, m+1):
            D[i][j] = min(
                D[i-1][j-1] + dist(s[i-1], t[j-1]),
                D[i][j-1] + gap_penalty,
                D[i-1][j] + gap_penalty
            )

    return D[n][m]


def origNWTW(s, t, dist, gap_penalty):
    n = len(s)
    m = len(t)
    D = [[None]*(m+1) for _ in range(n+1)]

    D[0][0] = 0

    for j in range(1, m+1):
        D[0][j] = D[0][j-1] + gap_penalty
    for i in range(1, n+1):
        D[i][0] = D[i-1][0] + gap_penalty

    for i in range(1, n+1):
        for j in range(1, m+1):
            d = dist(s[i-1], t[j-1])
            D[i][j] = min(
                D[i-1][j-1] + d,
                D[i][j-1] + gap_penalty,
                D[i-1][j] + gap_penalty,
                D[i][j-1] + d,
                D[i-1][j] + d
            )

    return D[n][m]


def simpleNWTW(s, t, dist, gap_penalty, window=None):
    n = len(s)
    m = len(t)

    if window is None:
        window = [(i, j) for j in range(0, m+1) for i in range(0, n+1)]

    # (distance, prev_i, prev_j, match)
    D = defaultdict(lambda: (float('inf'), None, None, False))
    D[0, 0] = (0, None, None, False)

    for i, j in window[1:]:
        if i == 0:
            D[0, j] = (D[0, j-1][0] + gap_penalty, 0, j-1, False)
        elif j == 0:
            D[i, 0] = (D[i-1, 0][0] + gap_penalty, i-1, 0, False)
        else:
            d = dist(s[i-1], t[j-1])
            D[i, j] = min(
                    (D[i-1, j-1][0] + 2*d, i-1, j-1, True),
                    (D[i, j-1][0] + d, i, j-1, True),
                    (D[i-1, j][0] + d, i-1, j, True),
                    (D[i, j-1][0] + gap_penalty, i , j-1, False),
                    (D[i-1, j][0] + gap_penalty, i-1, j, False),
                    key=lambda x: x[0]
                )

    i, j = n, m
    distance = D[i, j][0]
    path = []
    while True:
        path += [(i, j, D[i, j][3])]
        if i == 0 and j == 0:
            return distance, list(reversed(path))
        i, j = D[i, j][1], D[i, j][2]
        
        

def BDTW(s, t, dist, gap_penalty, window=None):
    n = len(s)
    m = len(t)
    
    # weights for diagonal, horizontal and vertical mapping
    dw, hw, vw = 3, 2, 2

    if window is None:
        window = [(i, j) for j in range(0, m+1) for i in range(0, n+1)]

    # (distance, prev_i, prev_j, match)
    D = defaultdict(lambda: (float('inf'), None, None, False))
    D[0, 0] = (0, None, None, False)

    for i, j in window[1:]:
        if i == 0:
            D[0, j] = (D[0, j-1][0] + gap_penalty, 0, j-1, False)
        elif j == 0:
            D[i, 0] = (D[i-1, 0][0] + gap_penalty, i-1, 0, False)
        else:
            d = dist(s[i-1], t[j-1])
            if i == n and j == m:
                D[i, j] = min(
                        (D[i-1, j-1][0] + dw*d, i-1, j-1, True),
                        (D[i, j-1][0] + vw*d, i, j-1, True),
                        (D[i-1, j][0] + hw*d, i-1, j, True),
                        (D[i, j-1][0] + gap_penalty, i , j-1, False),
                        (D[i-1, j][0] + gap_penalty, i-1, j, False),
                        key=lambda x: x[0]
                    )
            elif i == n:
                D[i, j] = min(
                        (D[i-1, j-1][0] + dw*d, i-1, j-1, True),
                        (D[i, j-1][0] + vw*d, i, j-1, True),
                        (D[i-1, j][0] + hw*d, i-1, j, True),
                        (D[i, j-1][0] + gap_penalty, i , j-1, False),
                        key=lambda x: x[0]
                    )
            elif j == m:
                D[i, j] = min(
                        (D[i-1, j-1][0] + dw*d, i-1, j-1, True),
                        (D[i, j-1][0] + vw*d, i, j-1, True),
                        (D[i-1, j][0] + hw*d, i-1, j, True),
                        (D[i-1, j][0] + gap_penalty, i-1, j, False),
                        key=lambda x: x[0]
                    )
            else:
                D[i, j] = min(
                        (D[i-1, j-1][0] + dw*d, i-1, j-1, True),
                        (D[i, j-1][0] + vw*d, i, j-1, True),
                        (D[i-1, j][0] + hw*d, i-1, j, True),
                        key=lambda x: x[0]
                    )

    i, j = n, m
    distance = D[i, j][0]
    path = []
    while True:
        path += [(i-1, j-1, D[i, j][3])]
        if i == 1 or j == 1:
            return distance, list(reversed(path))
        i, j = D[i, j][1], D[i, j][2]
    

if __name__ == '__main__':
    s = np.array([1,3,4,5,5,2]).reshape(-1, 1)
    t = np.array([1,2,4,1,6,6,3,2]).reshape(-1, 1)

    # print(DTW(s,t, lambda x,y: abs(x-y)))

    # print(FastDTW(s,t, lambda x,y: abs(x-y), 0))

    print(simpleNWTW(s,t, lambda x,y: abs(x-y), 1))

    # print(NW(s,t, lambda x,y: abs(x-y), 1))

    # print(NWTW(s,t, lambda x,y: abs(x-y), 1))
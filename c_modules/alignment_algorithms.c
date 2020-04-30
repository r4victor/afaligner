#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <float.h>
#include <stdio.h>


typedef struct {
    double distance;
    int prev_i;
    int prev_j;
} D_matrix_element;


// Returns warping path length.
// Writes warping path distance to the `path_distance`.
// Writes warping path to the `path_buffer`.
int DTWBD(
    double *s,  // first sequence of MFCC frames – n x l contiguous array
    double *t,  // second sequence of MFCC frames – m x l contiguous array
    int n,   // number of frames in first sequence
    int m,   // number of frames in second sequence
    int l,   // number of MFCCs per frame
    double skip_penalty,    // penalty for skipping one frame
    double *path_distance,  // place to store warping path distance
    int *path_buffer     // buffer to store resulting warping path – (n+m) x 2 contiguous array
);


double euclid_distance(double *x, double *y, int l);


double get_distance(D_matrix_element *D_matrix, int n, int m, int i, int j);


D_matrix_element get_best_candidate(D_matrix_element *candidates, int n);


void reverse_path(int *path, int path_len);


// Returns warping path length.
// Writes warping path distance to the `path_distance`.
// Writes warping path to the `path_buffer`.
int DTWBD(
    double *s,  // first sequence of MFCC frames – n x l contiguous array
    double *t,  // second sequence of MFCC frames – m x l contiguous array
    int n,   // number of frames in first sequence
    int m,   // number of frames in second sequence
    int l,   // number of MFCCs per frame
    double skip_penalty,    // penalty for skipping one frame
    double *path_distance,  // place to store warping path distance
    int *path_buffer     // buffer to store resulting warping path – (n+m) x 2 contiguous array
) {
    D_matrix_element *D_matrix = malloc(sizeof(D_matrix_element) * n * m);
    double min_path_distance;
    double cur_path_distance;
    int end_i = -1, end_j = -1;

    min_path_distance = skip_penalty * (n + m);

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            double d = euclid_distance(s+i*l, t+j*l, l);
            
            D_matrix_element candidates[] = {
                { skip_penalty * (i + j) + d, -1, -1 },
                { get_distance(D_matrix, n, m, i-1, j-1) + d, i-1, j-1 },
                { get_distance(D_matrix, n, m, i, j-1) + d, i, j-1 },
                { get_distance(D_matrix, n, m, i-1, j) + d, i-1, j },
            };

            D_matrix[i*m+j] = get_best_candidate(candidates, sizeof(candidates)/sizeof(D_matrix_element));

            cur_path_distance = D_matrix[i*m+j].distance + skip_penalty * (n - i + m - j - 2);

            if (cur_path_distance < min_path_distance) {
                min_path_distance = cur_path_distance;
                end_i = i;
                end_j = j;
            }
        }
    }

    int path_len = 0;
    D_matrix_element *e;
    *path_distance = min_path_distance;
    for (int i = end_i, j = end_j; i != -1; i = e->prev_i, j = e->prev_j) {
        e = &D_matrix[i*m+j];
        path_buffer[2*path_len] = i;
        path_buffer[2*path_len+1] = j;
        path_len++;
    }

    reverse_path(path_buffer, path_len);

    free(D_matrix);

    return path_len;
}


double euclid_distance(double *x, double *y, int l) {
    double sum;

    sum = 0;
    for (int i = 0; i < l; i++) {
        double v = x[i] - y[i];
        sum += v * v;
    }

    return sqrt(sum);
}


double get_distance(D_matrix_element *D_matrix, int n, int m, int i, int j) {
    if (i >= 0 && i < n && j >= 0 && j < m) {
        return D_matrix[i*m+j].distance;
    }

    return DBL_MAX;
}


D_matrix_element get_best_candidate(D_matrix_element *candidates, int n) {
    double min_distance = DBL_MAX;
    D_matrix_element best_candidate;

    for (int i = 0; i < n; i++) {
        if (candidates[i].distance < min_distance) {
            min_distance = candidates[i].distance;
            best_candidate = candidates[i];
        }
    }

    return best_candidate;
}


void reverse_path(int *path, int path_len) {
    for (int i = 0, j = path_len - 1; i < j; i++, j--) {
        int tmp_s = path[2*i];
        int tmp_t = path[2*i+1];
        path[2*i] = path[2*j];
        path[2*i+1] = path[2*j+1];
        path[2*j] = tmp_s;
        path[2*j+1] = tmp_t;
    }
}

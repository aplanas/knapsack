from cython.parallel import parallel, prange, threadid
from libc.stdlib cimport malloc, free
cimport openmp

import random


class SparseMatrix(object):
    def __init__(self):
        self.row = []

    def set(self, x, y):
        while x >= len(self.row):
            self.row.append([])

        r = self.row[x]
        interval = [y, y]
        try:
            interval = r[-1]
        except:
            pass

        if interval[1] == y - 1:
            interval[1] = y
        else:
            r.append([y, y])
            # print x, y

    def get(self, x, y):
        if x >= len(self.row):
            return 0

        r = self.row[x]
        return any(t[0] <= y <= t[1] for t in r)


def kpsolution(weights, capacity, keep):
    """Reconstruct the solution using the keep matrix."""
    solution = []

    # We go from (n, W) backtracking according to the keep matrix
    j = capacity

    for i in range(len(weights), 0, -1):
        if keep.get(i, j):
            solution.append(i-1)
            j = j - weights[i-1]

    solution.reverse()
    return solution


def knapsack(values, weights, int capacity):
    cdef int* _values = <int *>malloc(len(values) * sizeof(int))
    for i, x in enumerate(values):
        _values[i] = x

    cdef int* _weights = <int *>malloc(len(weights) * sizeof(int))
    for i, x in enumerate(weights):
        _weights[i] = x

    keep = _knapsack(_values, _weights, len(weights), capacity)
    return kpsolution(weights, capacity, keep)


cdef struct Tuple:
    int i
    int j


cdef int _kp_loop(int weight, int value, int j, int* previous_row, int* current_row) nogil:
    # If the weight of the i item is bigger than the limit j,
    # we can't carry it.
    if weight > j:
        current_row[j] = previous_row[j]
    else:
        # Get the maximum value when we leave or we carry the
        # i item.
        #
        # m[i-1][j]: maximun value if we don't take the item
        #
        # m[i-1][j-weight[i]] + values[i]: if we the item, the
        #   new value is the value of the item plus the
                #   maximum value when wehave enough room for this
        #   item.
        #
        current_row[j] = max(previous_row[j],
                             previous_row[j-weight] + value)
        if current_row[j] != previous_row[j]:
            return 1
        return 0


cdef _knapsack(int* values, int* weights, int lweights, int capacity):
    """Implement the 0/1 knapsack solver."""

    # We use the dynamic programming pseudo-polynomial time algorithm

    cdef int i, j, local_i
    cdef int _i

    # Initialize the matrix
    cdef int *previous_row = <int *>malloc((capacity+1) * sizeof(int))
    cdef int *current_row = <int *>malloc((capacity+1) * sizeof(int))

    for i in range(capacity+1):
        previous_row[i] = 0
        current_row[i] = 0

    keep = SparseMatrix()

    cdef Tuple** keep_local = <Tuple **>malloc((openmp.omp_get_max_threads()) * sizeof(Tuple*))
    cdef int* keep_local_counter = <int *>malloc((openmp.omp_get_max_threads()) * sizeof(int))

    cdef Tuple* _keep_local

    for i in range(openmp.omp_get_max_threads()):
        keep_local[i] = <Tuple *>malloc((capacity+1) * sizeof(Tuple))
        keep_local_counter[i] = 0

    # Build the rest of the table. In every iteration m[i][j] will
    # store the maximum value that we can carry using a combination of
    # items of {1, ..., i}, with weight at most of j.

    for i in range(1, lweights+1):
        # print i
        with nogil, parallel():
            _keep_local = keep_local[threadid()]
            for j in prange(capacity+1):
                if _kp_loop(weights[i-1], values[i-1], j, previous_row, current_row):
                    _i = keep_local_counter[threadid()]
                    _keep_local[_i].i = i
                    _keep_local[_i].j = j
                    keep_local_counter[threadid()] += 1

        current_row, previous_row = previous_row, current_row

        for t in range(openmp.omp_get_max_threads()):
            for c in range(keep_local_counter[t]):
                # print keep_local[t][c].i, keep_local[t][c].j
                keep.set(keep_local[t][c].i, keep_local[t][c].j)
            keep_local_counter[t] = 0

    for t in range(openmp.omp_get_max_threads()):
        free(keep_local[t])
    free(keep_local)
    free(keep_local_counter)

    free(current_row)
    free(previous_row)

    return keep

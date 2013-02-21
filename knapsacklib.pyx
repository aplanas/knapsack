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

    def merge(self, x, y1, y2):
        # we cheat
        while x >= len(self.row):
            self.row.append([])

        r = self.row[x]
        interval = [y1, y2]
        try:
            interval = r[-1]
        except:
            r.append(interval)
            return

        if interval[1] == y1 - 1:
            interval[1] = y2
        else:
            r.append([y1, y2])

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


cdef int _kp_insert(int *array, int index, int value) nogil:
    #fprintf(stdout, "insert %x %d %d\n", array, index, value)
    if array[index] == -1: # empty - index == 0
        array[index] = value
        array[index+1] = value
        array[index+2] = -1
        # we need to point to the end of the sequence
        return index + 1

    if array[index] == value - 1: # enlarge the sequence
        array[index] = value
        return index

    # sequence does not match - append a new one
    array[index+1] = value
    array[index+2] = value
    array[index+3] = -1
    return index + 2


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

    cdef int** keep_local = <int **>malloc((openmp.omp_get_max_threads()) * sizeof(int*))
    cdef int* keep_local_index = <int *>malloc((openmp.omp_get_max_threads()) * sizeof(int))

    cdef int* _keep_local
    cdef int _keep_index

    # the worst case for the size of this array is if the pattern is 0-1-0-1-0     
    # then we need to keep for every 2nd number two ints. So to make sure we're 
    # not running into this, we add another 10
    cdef int max_size = capacity + 10
    for i in range(openmp.omp_get_max_threads()):
        keep_local[i] = <int *>malloc(max_size * sizeof(int))

    # Build the rest of the table. In every iteration m[i][j] will
    # store the maximum value that we can carry using a combination of
    # items of {1, ..., i}, with weight at most of j.

    for i in range(1, lweights+1):
        #print i
        with nogil, parallel():
            _i = threadid()
            # mark the start of the index
            _keep_local = keep_local[_i]
            _keep_local[0] = -1
            keep_local_index[_i] = 0
            for j in prange(capacity+1, schedule='static'):
                if _kp_loop(weights[i-1], values[i-1], j, previous_row, current_row):
                    keep_local_index[_i] = _kp_insert(_keep_local, keep_local_index[_i], j)

        current_row, previous_row = previous_row, current_row

        for t in range(openmp.omp_get_max_threads()):
            c = 0
            while keep_local[t][c] != -1:
                #print t, i, keep_local[t][c], keep_local[t][c+1]
                keep.merge(i, keep_local[t][c], keep_local[t][c+1])
                c += 2

    for t in range(openmp.omp_get_max_threads()):
        free(keep_local[t])
    free(keep_local)
    free(keep_local_index)

    free(current_row)
    free(previous_row)

    return keep

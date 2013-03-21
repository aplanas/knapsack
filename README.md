knapsack
========

0/1 KP resolution for openSUSE mirrors

openSUSE is using a set of mirrors that use rsync to fetch the data. In order to optimize the process, we use the
knapsack algorithm (http://en.wikipedia.org/wiki/Knapsack_problem). This implementation use Cython and prange() to
parallelize the computations, and a special sparse matrix to gather the solution.

knapsack
========

0/1 KP resolution for openSUSE mirrors

openSUSE is using a set of mirrors that use rsync to fetch the
data. In order to optimize the process, we use the knapsack algorithm
(http://en.wikipedia.org/wiki/Knapsack_problem). This implementation
use Cython and prange() to parallelize the computations, and a special
sparse matrix to gather the solution.

The input of this script is basically two lists: one with the value of
the resource (file), and other the weight of the resource (file). The
weight is usually the size of the file, and the value is some metric
about the importance of the file, like the number of hits that this
file had in the previous week. Both inputs are adapted for openSUSE
infrastructure and need, but can be easily changed for other
scenarios.


knapsack.py
-----------

This is the main script. It takes the list of values and weights and
resolve the basic KP problem. The output is the list of files that
must be in the knapsack. Both input files use the same format:

    1000 full_file_path

The initial number must be an integer and can represent the size of
the value of the resource. So, if we want to calculate the solution
for a 10Gb knapsack:

    python knapsack.py --price price_list.txt --size size_list.txt --wsize 10240

Note that the size of the knapsack is in megabytes and not in
bytes. Internally, the algorithm build and internal matrix using
megabytes achieve faster solutions, but loosing some precision. The
complexity of the algorithm is O(nw) where n is the number of files
and w the size of the knapsack. So, reducing the resolution of the
size we decrease the total amount of time spent.

To avoid the precision problem (we can get bigger KP than expected),
we have implemented a linear regression model to predict the correct
size of the final solution. You can enable this feature using the
--fixsize option.


Environment
-----------

The rest of the script are only to create and process the size and
price files, reading information from external sources and services
like [MirrorBrain] or the logs from the Apache web server. They are
useless for a generic solution, but can server as a initial point to
develop your own environment to feed the KP algorithm.

  [1]: http://www.mirrorbrain.org/ "MirrorBrain"

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_module = Extension(
    'knapsack.cknapsack',
    ['knapsack/cknapsack.pyx'],
    extra_compile_args=['-fopenmp'],
    extra_link_args=['-fopenmp'],
)

setup(
    name='knapsack',
    version='1.0',
    description='Knapsack algorithm for openSUSE mirrors',
    author='Alberto Planas',
    author_email='aplanas@suse.de',
    py_modules=['knapsack'],
    scripts=['disk_size_groups', 'kp', 'merge_payload',
             'remove_package_version', 'remove_time_filter_new',
             'get_file', 'run-when', 'update-rsync', 'disk_size',
             'full-kp', 'mirror_brain', 'payload', 'prepare-kp',
             'run-server', 'user-agents'],
    cmdclass={'build_ext': build_ext},
    ext_modules=[ext_module],
)

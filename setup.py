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
    version='0.2.0',
    description='Knapsack algorithm for openSUSE mirrors',
    author='Alberto Planas',
    author_email='aplanas@suse.de',
    url='https://github.com/openSUSE/knapsack',
    packages=['knapsack'],
    scripts=['disk_size', 'disk_size_groups', 'full-kp', 'get_path', 'kp',
             'merge_payload', 'mirror_brain', 'payload', 'prepare-kp',
             'remove_package_version', 'remove_time_filter_new', 'run-server',
             'run-when', 'update-rsync', 'update-rsync-notify.py',
             'user-agents'],
    data_files=[('data', ['bots.txt']),
                ('/etc', ['kp.cfg.sample'])],
    cmdclass={'build_ext': build_ext},
    ext_modules=[ext_module],
)

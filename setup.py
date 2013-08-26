from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_module = Extension(
    "knapsacklib",
    ["knapsacklib.pyx"],
    extra_compile_args=['-fopenmp'],
    extra_link_args=['-fopenmp'],
)

setup(
    name='knapsack',
    version='1.0',
    description='Knapsack alogrithm for openSUSE mirrors',
    author='Alberto Planas',
    author_email='aplanas@suse.de',
    cmdclass={'build_ext': build_ext},
    # ext_modules = [Extension("knapsacklib", ["knapsacklib.pyx"])]
    ext_modules=[ext_module],
)

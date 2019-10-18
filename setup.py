from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))


v_temp = {}
with open("bw_default_backend/version.py") as fp:
    exec(fp.read(), v_temp)
version = ".".join((str(x) for x in v_temp['version']))


setup(
    name='bw_default_backend',
    version=version,
    description='Default backend for Brightway Life Cycle Assessment framework',
    long_description=open(os.path.join(here, "README.md")).read(),
    url='https://github.com/brightway-lca/bw_default_backend',
    author='Chris Mutel',
    author_email='cmutel@gmail.com',
    license=open(os.path.join(here, "LICENSE.txt")).read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'peewee',
        'stats_arrays',
        'numpy',
        'wrapt',
        'brightway_projects',
        "bw_processing",
    ],
)

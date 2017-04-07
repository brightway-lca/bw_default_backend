from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='bw-default-backend',
    version='0.1',
    description='Default backend for Brightway Life Cycle Assessment framework',
    long_description=open(os.path.join(here, "README.md")).read(),
    url='https://github.com/pypa/sampleproject',
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
    ],
)

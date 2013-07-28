# -*- coding: utf-8 -*-
from __future__ import with_statement
from setuptools import setup


def get_version(fname='flake8/__init__.py'):
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def get_long_description():
    descr = []
    for fname in ('README.rst', 'CHANGES.rst'):
        with open(fname) as f:
            descr.append(f.read())
    return '\n\n'.join(descr)


setup(
    name="flake8",
    license="MIT",
    version=get_version(),
    description="the modular source code checker: pep8, pyflakes and co",
    long_description=get_long_description(),
    author="Tarek Ziade",
    author_email="tarek@ziade.org",
    maintainer="Ian Cordasco",
    maintainer_email="graffatcolmingov@gmail.com",
    url="http://bitbucket.org/tarek/flake8",
    packages=["flake8", "flake8.tests"],
    install_requires=[
        "pyflakes >= 0.7.3",
        "pep8 >= 1.4.6",
        "mccabe >= 0.2.1",
    ],
    entry_points={
        'distutils.commands': ['flake8 = flake8.main:Flake8Command'],
        'console_scripts': ['flake8 = flake8.main:main'],
        'flake8.extension': [
            'F = flake8._pyflakes:FlakesChecker',
        ],
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
)

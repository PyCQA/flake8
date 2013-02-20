from setuptools import setup

from flake8 import __version__

README = open('README.rst').read()

setup(
    name="flake8",
    license="MIT",
    version=__version__,
    description="code checking using pep8 and pyflakes",
    long_description=README,
    author="Tarek Ziade",
    author_email="tarek@ziade.org",
    maintainer="Ian Cordasco",
    maintainer_email="graffatcolmingov@gmail.com",
    url="http://bitbucket.org/tarek/flake8",
    packages=["flake8", "flake8.tests"],
    install_requires=[
        "setuptools",
        "pyflakes >= 0.6.1",
        "pep8 >= 1.4.2",
    ],
    entry_points={
        'distutils.commands': ['flake8 = flake8.main:Flake8Command'],
        'console_scripts': ['flake8 = flake8.main:main'],
        'flake8.extension': [
            'F = flake8._pyflakes:FlakesChecker',
            'C90 = flake8.mccabe:McCabeChecker',
        ],
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    tests_require=['nose'],
    test_suite='nose.collector',
)

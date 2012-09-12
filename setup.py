import sys

ispy3 = sys.version_info[0] == 3

kwargs = {}
if ispy3:
    from distutils.core import setup    # NOQA
else:
    try:
        from setuptools import setup    # NOQA
        kwargs = {
            'tests_require': ['nose'],
            'test_suite': 'nose.collector',
        }
    except ImportError:
        from distutils.core import setup   # NOQA

from flake8 import __version__

README = open('README').read()

setup(
    name="flake8",
    license="MIT",
    version=__version__,
    description="code checking using pep8 and pyflakes",
    author="Tarek Ziade",
    author_email="tarek@ziade.org",
    url="http://bitbucket.org/tarek/flake8",
    packages=["flake8", "flake8.tests"],
    scripts=["flake8/flake8"],
    long_description=README,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
        ],
    **kwargs)

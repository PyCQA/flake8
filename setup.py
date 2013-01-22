import sys
import os

ispy3 = sys.version_info[0] == 3
iswin = os.name == 'nt'

kwargs = {}
scripts = ["flake8/flake8"]
if ispy3:
    from distutils.core import setup    # NOQA
    if iswin:
        scripts.append("scripts/flake8.cmd")
else:
    try:
        from setuptools import setup    # NOQA
        kwargs = {
            'entry_points': {
                'distutils.commands': ['flake8 = flake8.main:Flake8Command'],
                'console_scripts': ['flake8 = flake8.main:main']
            },
            'tests_require': ['nose'],
            'test_suite': 'nose.collector',
        }
    except ImportError:
        from distutils.core import setup   # NOQA
        if iswin:
            scripts.append("scripts/flake8.cmd")

from flake8 import __version__

README = open('README.rst').read()

setup(
    name="flake8",
    license="MIT",
    version=__version__,
    description="code checking using pep8 and pyflakes",
    author="Tarek Ziade",
    author_email="tarek@ziade.org",
    maintainer="Ian Cordasco",
    maintainer_email="graffatcolmingov@gmail.com",
    url="http://bitbucket.org/tarek/flake8",
    packages=["flake8", "flake8.tests"],
    scripts=scripts,
    install_requires=["flakey (==2.0)",  "pep8 (==1.4.1)"],
    long_description=README,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    **kwargs
)

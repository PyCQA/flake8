try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

README = open('README').read()

setup(
    name="flake8",
    license="MIT",
    version="1.1",
    description="code checking using pep8 and pyflakes",
    author="Tarek Ziade",
    author_email="tarek@ziade.org",
    url="http://bitbucket.org/tarek/flake8",
    packages=["flake8", "flake8.tests"],
    scripts=["bin/flake8"],
    long_description=README,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
        ])

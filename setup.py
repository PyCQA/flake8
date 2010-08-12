from distutils.core import setup

setup(
    name="flake8",
    license="MIT",
    version="0.1",
    description="code checking",
    author="Tarek Ziade",
    url="http://bitbucket.org/tarek/flake8",
    packages=["flake8", "flake8.scripts", "flake8.test"],
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

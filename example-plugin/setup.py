from __future__ import annotations

import setuptools

setuptools.setup(
    name="flake8-example-plugin",
    license="MIT",
    version="1.0.0",
    description="Example plugin to Flake8",
    author="Ian Cordasco",
    author_email="graffatcolmingov@gmail.com",
    url="https://github.com/pycqa/flake8",
    package_dir={"": "src/"},
    packages=["flake8_example_plugin"],
    entry_points={
        "flake8.extension": [
            "X1 = flake8_example_plugin:ExampleOne",
            "X2 = flake8_example_plugin:ExampleTwo",
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)

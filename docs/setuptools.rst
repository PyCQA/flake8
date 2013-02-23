setuptools integration
======================

If setuptools is available, Flake8 provides a command that checks the
Python files declared by your project.  To use it, add flake8 to your
setup_requires::

    setup(
        name="project",
        packages=["project"],

        setup_requires=[
            "flake8"
        ]
    )

Running ``python setup.py flake8`` on the command line will check the
files listed in your ``py_modules`` and ``packages``.  If any warning
is found, the command will exit with an error code::

    $ python setup.py flake8

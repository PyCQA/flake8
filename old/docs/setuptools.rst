Setuptools integration
======================

Upon installation, Flake8 enables a setuptools command that checks Python 
files declared by your project. 

Running ``python setup.py flake8`` on the command line will check the files 
listed in your ``py_modules`` and ``packages``.  If any warning is found, 
the command will exit with an error code::

    $ python setup.py flake8

Also, to allow users to be able to use the command without having to install 
flake8 themselves, add flake8 to the setup_requires of your setup() like so::

    setup(
        name="project",
        packages=["project"],

        setup_requires=[
            "flake8"
        ]
    )



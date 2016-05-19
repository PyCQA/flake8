.. flake8 documentation master file, created by
   sphinx-quickstart on Tue Jan 19 07:14:10 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flake8: Your Tool For Style Guide Enforcement
=============================================

Installation
------------

To install Flake8, open an interactive shell and run:

.. code::

    python<version> -m pip install flake8

If you want Flake8 to be installed for your default Python installation, you
can instead use:

.. code::

    python -m pip install flake8

.. note::

    It is **very** important to install Flake8 on the *correct* version of
    Python for your needs. If you want Flake8 to properly parse new language
    features in Python 3.5 (for example), you need it to be installed on 3.5
    for those features to be understandable. In many ways, Flake8 is tied to
    the version of Python on which it runs.

Quickstart
----------

To start using Flake8, open an interactive shell and run:

.. code::

    flake8 path/to/code/to/check.py
    # or
    flake8 path/to/code/

.. note::

    If you have installed Flake8 on a particular version of Python (or on
    several versions), it may be best to instead run ``python<version> -m
    flake8``.

If you only want to see the instances of a specific warning or error, you can
*select* that error like so:

.. code::

    flake8 --select <Error> path/to/code/

Alternatively, if you want to *ignore* only one specific warning or error:

.. code::

    flake8 --ignore <Error> path/to/code/

Please read our user guide for more information about how to use and configure
Flake8.

User Guide
----------

.. toctree::
    :maxdepth: 2

    user/index

Plugin Developer Guide
----------------------

.. toctree::
    :maxdepth: 2

    dev/index

Developer Guide
---------------

.. toctree::
    :maxdepth: 2

    internal/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

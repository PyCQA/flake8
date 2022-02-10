.. flake8 documentation master file, created by
   sphinx-quickstart on Tue Jan 19 07:14:10 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===============================================
 Flake8: Your Tool For Style Guide Enforcement
===============================================

Quickstart
==========

.. _installation-guide:

Installation
------------

To install |Flake8|, open an interactive shell and run:

.. code::

    python<version> -m pip install flake8

If you want |Flake8| to be installed for your default Python installation, you
can instead use:

.. code::

    python -m pip install flake8

.. note::

    It is **very** important to install |Flake8| on the *correct* version of
    Python for your needs. If you want |Flake8| to properly parse new language
    features in Python 3.5 (for example), you need it to be installed on 3.5
    for |Flake8| to understand those features. In many ways, Flake8 is tied to
    the version of Python on which it runs.

Using Flake8
------------

To start using |Flake8|, open an interactive shell and run:

.. code::

    flake8 path/to/code/to/check.py
    # or
    flake8 path/to/code/

.. note::

    If you have installed |Flake8| on a particular version of Python (or on
    several versions), it may be best to instead run ``python<version> -m
    flake8``.

If you only want to see the instances of a specific warning or error, you can
*select* that error like so:

.. code::

    flake8 --select E123,W503 path/to/code/

Alternatively, if you want to *ignore* only one specific warning or error:

.. code::

    flake8 --ignore E24,W504 path/to/code/

Please read our user guide for more information about how to use and configure
|Flake8|.

FAQ and Glossary
================

.. toctree::
    :maxdepth: 2

    faq
    glossary

User Guide
==========

All users of |Flake8| should read this portion of the documentation. This
provides examples and documentation around |Flake8|'s assortment of options
and how to specify them on the command-line or in configuration files.

.. toctree::
    :maxdepth: 2

    user/index

Plugin Developer Guide
======================

If you're maintaining a plugin for |Flake8| or creating a new one, you should
read this section of the documentation. It explains how you can write your
plugins and distribute them to others.

.. toctree::
    :maxdepth: 2

    plugin-development/index

Contributor Guide
=================

If you are reading |Flake8|'s source code for fun or looking to contribute,
you should read this portion of the documentation. This is a mix of documenting
the internal-only interfaces |Flake8| and documenting reasoning for Flake8's
design.

.. toctree::
    :maxdepth: 2

    internal/index

Release Notes and History
=========================

.. toctree::
    :maxdepth: 2

    release-notes/index

General Indices
===============

* :ref:`genindex`
* :ref:`Index of Documented Public Modules <modindex>`
* :ref:`Glossary of terms <glossary>`

.. _invocation:

=================
 Invoking Flake8
=================

Once you have :ref:`installed <installation-guide>` |Flake8|, you can begin
using it. Most of the time, you will be able to generically invoke |Flake8|
like so:

.. prompt:: bash

    flake8 ...

Where you simply allow the shell running in your terminal to locate |Flake8|.
In some cases, though, you may have installed |Flake8| for multiple versions
of Python (e.g., Python 3.13 and Python 3.14) and you need to call a specific
version. In that case, you will have much better results using:

.. prompt:: bash

    python3.13 -m flake8

Or

.. prompt:: bash

    python3.14 -m flake8

Since that will tell the correct version of Python to run |Flake8|.

.. note::

    Installing |Flake8| once will not install it on both Python 3.13 and
    Python 3.14. It will only install it for the version of Python that
    is running pip.

It is also possible to specify command-line options directly to |Flake8|:

.. prompt:: bash

    flake8 --select E123

Or

.. prompt:: bash

    python<version> -m flake8 --select E123

.. note::

    This is the last time we will show both versions of an invocation.
    From now on, we'll simply use ``flake8`` and assume that the user
    knows they can instead use ``python<version> -m flake8``.

It's also possible to narrow what |Flake8| will try to check by specifying
exactly the paths and directories you want it to check. Let's assume that
we have a directory with python files and sub-directories which have python
files (and may have more sub-directories) called ``my_project``. Then if
we only want errors from files found inside ``my_project`` we can do:

.. prompt:: bash

    flake8 my_project

And if we only want certain errors (e.g., ``E123``) from files in that
directory we can also do:

.. prompt:: bash

    flake8 --select E123 my_project

If you want to explore more options that can be passed on the command-line,
you can use the ``--help`` option:

.. prompt:: bash

    flake8 --help

And you should see something like:

.. code::

    Usage: flake8 [options] file file ...

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit

      ...

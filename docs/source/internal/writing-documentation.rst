.. _docs-style:

==================================
 Writing Documentation for Flake8
==================================

The maintainers of |Flake8| believe strongly in benefit of style guides.
Hence, for all contributors who wish to work on our documentation, we've
put together a loose set of guidelines and best practices when adding to
our documentation.


View the docs locally before submitting
=======================================

You can and should generate the docs locally before you submit a pull request
with your changes. You can build the docs by running:

.. prompt:: bash

    tox -e docs

From the directory containing the ``tox.ini`` file (which also contains the
``docs/`` directory that this file lives in).

.. note::

    If the docs don't build locally, they will not build in our continuous
    integration system. We will generally not merge any pull request that
    fails continuous integration.


Run the docs linter tests before submitting
===========================================

You should run the ``doc8`` linter job before you're ready to commit and fix
any errors found.


Capitalize Flake8 in prose
==========================

We believe that by capitalizing |Flake8| in prose, we can help reduce
confusion between the command-line usage of ``flake8`` and the project.

We also have defined a global replacement ``|Flake8|`` that should be used
and will replace each instance with ``:program:`Flake8```.


Use the prompt directive for command-line examples
==================================================

When documenting something on the command-line, use the ``.. prompt::``
directive to make it easier for users to copy and paste into their terminal.

Example:

.. code-block:: restructuredtext

    .. prompt:: bash

        flake8 --select E123,W503 dir/
        flake8 --ignore E24,W504 dir


Wrap lines around 79 characters
===============================

We use a maximum line-length in our documentation that is similar to the
default in |Flake8|. Please wrap lines at 79 characters (or less).


Use two new-lines before new sections
=====================================

After the final paragraph of a section and before the next section title,
use two new-lines to separate them. This makes reading the plain-text
document a little nicer. Sphinx ignores these when rendering so they have
no semantic meaning.

Example:

.. code-block:: restructuredtext

    Section Header
    ==============

    Paragraph.


    Next Section Header
    ===================

    Paragraph.


Surround document titles with equal symbols
===========================================

To indicate the title of a document, we place an equal number of ``=`` symbols
on the lines before and after the title. For example:

.. code-block:: restructuredtext

    ==================================
     Writing Documentation for Flake8
    ==================================

Note also that we "center" the title by adding a leading space and having
extra ``=`` symbols at the end of those lines.


Use the option template for new options
=======================================

All of |Flake8|'s command-line options are documented in the User Guide. Each
option is documented individually using the ``.. option::`` directive provided
by Sphinx. At the top of the document, in a reStructuredText comment, is a
template that should be copied and pasted into place when documening new
options.

.. note::

    The ordering of the options page is the order that options are printed
    in the output of:

    .. prompt:: bash

        flake8 --help

    Please insert your option documentation according to that order.


Use anchors for easy reference linking
======================================

Use link anchors to allow for other areas of the documentation to use the
``:ref:`` role for intralinking documentation. Example:

.. code-block:: restructuredtext

    .. _use-anchors:

    Use anchors for easy reference linking
    ======================================

.. code-block:: restructuredtext

    Somewhere in this paragraph we will :ref:`reference anchors
    <use-anchors>`.

.. note::

    You do not need to provide custom text for the ``:ref:`` if the title of
    the section has a title that is sufficient.


Keep your audience in mind
==========================

|Flake8|'s documentation has three distinct (but not separate) audiences:

#. Users

#. Plugin Developers

#. Flake8 Developers and Contributors

At the moment, you're one of the third group (because you're contributing
or thinking of contributing).

Consider that most Users aren't very interested in the internal working of
|Flake8|. When writing for Users, focus on how to do something or the
behaviour of a certain piece of configuration or invocation.

Plugin developers will only care about the internals of |Flake8| as much as
they will have to interact with that. Keep discussions of internal to the
mininmum required.

Finally, Flake8 Developers and Contributors need to know how everything fits
together. We don't need detail about every line of code, but cogent
explanations and design specifications will help future developers understand
the Hows and Whys of |Flake8|'s internal design.

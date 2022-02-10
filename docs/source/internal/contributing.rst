========================
 Contributing to Flake8
========================

There are many ways to contribute to |Flake8|, and we encourage them all:

- contributing bug reports and feature requests

- contributing documentation (and yes that includes this document)

- reviewing and triaging bugs and merge requests

Before you go any further, please allow me to reassure you that I do want
*your* contribution. If you think your contribution might not be valuable, I
reassure you that any help you can provide *is* valuable.


Code of Conduct
===============

|Flake8| adheres to the `Python Code Quality Authority's Code of Conduct`_.
Any violations of the Code of Conduct should be reported to Ian Stapleton
Cordasco (graffatcolmingov [at] gmail [dot] com).


Setting Up A Development Environment
====================================

To contribute to |Flake8|'s development, you simply need:

- Python (one of the versions we support)

- `tox`_

  We suggest installing this like:

  .. prompt:: bash

        pip install --user tox

  Or

  .. prompt:: bash

        python<version> -m pip install --user tox

- your favorite editor


Filing a Bug
============

When filing a bug against |Flake8|, please fill out the issue template as it
is provided to you by `GitHub`_. If your bug is in reference to one of the
checks that |Flake8| reports by default, please do not report them to |Flake8|
unless |Flake8| is doing something to prevent the check from running or you
have some reason to believe |Flake8| is inhibiting the effectiveness of the
check.

**Please search for closed and open bug reports before opening new ones.**

All bug reports about checks should go to their respective projects:

- Error codes starting with ``E`` and ``W`` should be reported to
  `pycodestyle`_.

- Error codes starting with ``F`` should be reported to `pyflakes`_

- Error codes starting with ``C`` should be reported to `mccabe`_


Requesting a New Feature
========================

When requesting a new feature in |Flake8|, please fill out the issue template.
Please also note if there are any existing alternatives to your new feature
either via plugins, or combining command-line options. Please provide example
use cases. For example, do not ask for a feature like this:

    I need feature frobulate for my job.

Instead ask:

    I need |Flake8| to frobulate these files because my team expects them to
    frobulated but |Flake8| currently does not frobulate them. We tried using
    ``--filename`` but we could not create a pattern that worked.

The more you explain about *why* you need a feature, the more likely we are to
understand your needs and help you to the best of our ability.


Contributing Documentation
==========================

To contribute to |Flake8|'s documentation, you might want to first read a
little about reStructuredText or Sphinx. |Flake8| has a :ref:`guide of best
practices <docs-style>` when contributing to our documentation. For the most
part, you should be fine following the structure and style of the rest of
|Flake8|'s documentation.

All of |Flake8|'s documentation is written in reStructuredText and rendered by
Sphinx. The source (reStructuredText) lives in ``docs/source/``. To build
the documentation the way our Continuous Integration does, run:

.. prompt:: bash

    tox -e docs

To view the documentation locally, you can also run:

.. prompt:: bash

    tox -e serve-docs

You can run the latter in a separate terminal and continuously re-run the
documentation generation and refresh the documentation you're working on.

.. note::

    We lint our documentation just like we lint our code.
    You should also run:

    .. prompt:: bash

        tox -e linters

    After making changes and before pushing them to ensure that they will
    pass our CI tests.


Contributing Code
=================

|Flake8| development happens on `GitHub`_. Code contributions should be
submitted there.

Merge requests should:

- Fix one issue and fix it well

  Fix the issue, but do not include extraneous refactoring or code
  reformatting. In other words, keep the diff short, but only as short
  as is necessary to fix the bug appropriately and add sufficient testing
  around it. Long diffs are fine, so long as everything that it includes
  is necessary to the purpose of the merge request.

- Have descriptive titles and descriptions

  Searching old merge requests is made easier when a merge request is well
  described.

- Have commits that follow this style:

  .. code::

        Create a short title that is 50 characters long

        Ensure the title and commit message use the imperative voice. The
        commit and you are doing something. Also, please ensure that the
        body of the commit message does not exceed 72 characters.

        The body may have multiple paragraphs as necessary.

        The final line of the body references the issue appropriately.

- Follow the guidelines in :ref:`writing-code`

- Avoid having :code:`.gitignore` file in your PR

  Changes to :code:`.gitignore` will rarely be accepted.

  If you need to add files to :code:`.gitignore` you have multiple options

  - Create a global :code:`.gitignore` file
  - Create/update :code:`.git/info/exclude` file.

  Both these options are explained in detail `here <https://help.github.com/en/articles/ignoring-files#create-a-global-gitignore>`_


Reviewing and Triaging Issues and Merge Requests
================================================

When reviewing other people's merge requests and issues, please be
**especially** mindful of how the words you choose can be read by someone
else. We strive for professional code reviews that do not insult the
contributor's intelligence or impugn their character. The code review
should be focused on the code, its effectiveness, and whether it is
appropriate for |Flake8|.

If you have the ability to edit an issue or merge request's labels, please do
so to make search and prioritization easier.

|Flake8| uses milestones with both issues and merge requests. This provides
direction for other contributors about when an issue or merge request will be
delivered.


.. links
.. _Python Code Quality Authority's Code of Conduct:
    https://meta.pycqa.org/code-of-conduct.html

.. _tox:
    https://tox.readthedocs.io/

.. _GitHub:
    https://github.com/pycqa/flake8

.. _pycodestyle:
    https://github.com/pycqa/pycodestyle

.. _pyflakes:
    https://github.com/pyflakes/pyflakes

.. _mccabe:
    https://github.com/pycqa/mccabe

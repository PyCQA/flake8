==================
 Releasing Flake8
==================

There is not much that is hard to find about how |Flake8| is released.

- We use **major** releases (e.g., 2.0.0, 3.0.0, etc.) for big releases (e.g.,
  large scale refactors). This can also contain dependency version changes.

- We use **minor** releases (e.g., 2.1.0, 2.2.0, 3.1.0, 3.2.0, etc.) for
  releases that contain features and dependency version changes.

- We use **patch** releases (e.g., 2.1.1, 2.1.2, 3.0.1, 3.0.10, etc.) for
  releases that contain *only* bug fixes. These *never* contain changes to
  dependency version constraints.


Process
=======

To prepare a release, we create a file in :file:`docs/source/releases/` named:
``{{ release_number }}.rst`` (e.g., ``3.0.0.rst``). We note bug fixes,
improvements, and dependency version changes as well as other items of note
for users.

Before releasing, the following tox test environments must pass:

- Python 2.7 (a.k.a., ``tox -e py27``)

- Python 3.4 (a.k.a., ``tox -e py34``)

- Python 3.5 (a.k.a., ``tox -e py35``)

- PyPy (a.k.a., ``tox -e pypy``)

- Linters (a.k.a., ``tox -e linters``)

We tag the most recent commit that passes those items and contains our release
notes.

Finally, we run ``tox -e release`` to build source distributions (e.g.,
``flake8-3.0.0.tar.gz``), universal wheels, and upload them to PyPI with
Twine.

==================
 Releasing Flake8
==================

There is not much that is hard to find about how |Flake8| is released.

- We use **major** releases (e.g., 2.0.0, 3.0.0, etc.) for big, potentially
  backwards incompatible, releases.

- We use **minor** releases (e.g., 2.1.0, 2.2.0, 3.1.0, 3.2.0, etc.) for
  releases that contain features and dependency version changes.

- We use **patch** releases (e.g., 2.1.1, 2.1.2, 3.0.1, 3.0.10, etc.) for
  releases that contain *only* bug fixes.

In this sense we follow semantic versioning. But we follow it as more of a set
of guidelines. We're also not perfect, so we may make mistakes, and that's
fine.


Major Releases
==============

Major releases are often associated with backwards incompatibility. |Flake8|
hopes to avoid those, but will occasionally need them.

Historically, |Flake8| has generated major releases for:

- Unvendoring dependencies (2.0)

- Large scale refactoring (2.0, 3.0, 5.0)

- Subtly breaking CLI changes (3.0, 4.0, 5.0)

- Breaking changes to its plugin interface (3.0)

Major releases can also contain:

- Bug fixes (which may have backwards incompatible solutions)

- New features

- Dependency changes


Minor Releases
==============

Minor releases often have new features in them, which we define roughly as:

- New command-line flags

- New behaviour that does not break backwards compatibility

- New errors detected by dependencies, e.g., by raising the upper limit on
  PyFlakes we introduce F405

- Bug fixes


Patch Releases
==============

Patch releases should only ever have bug fixes in them.

We do not update dependency constraints in patch releases. If you do not
install |Flake8| from PyPI, there is a chance that your packager is using
different requirements. Some downstream redistributors have been known to
force a new version of PyFlakes, pep8/PyCodestyle, or McCabe into place.
Occasionally this will cause breakage when using |Flake8|. There is little
we can do to help you in those cases.


Process
=======

To prepare a release, we create a file in :file:`docs/source/release-notes/`
named: ``{{ release_number }}.rst`` (e.g., ``3.0.0.rst``). We note bug fixes,
improvements, and dependency version changes as well as other items of note
for users.

Before releasing, the following tox test environments must pass:

- Python 3.6 (a.k.a., ``tox -e py36``)

- Python 3.7 (a.k.a., ``tox -e py37``)

- PyPy 3 (a.k.a., ``tox -e pypy3``)

- Linters (a.k.a., ``tox -e linters``)

We tag the most recent commit that passes those items and contains our release
notes.

Finally, we run ``tox -e release`` to build source distributions (e.g.,
``flake8-3.0.0.tar.gz``), universal wheels, and upload them to PyPI with
Twine.

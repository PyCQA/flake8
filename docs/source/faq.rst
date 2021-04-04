============================
 Frequently Asked Questions
============================

When is Flake8 released?
========================

|Flake8| is released *as necessary*. Sometimes there are specific goals and
drives to get to a release. Usually, we release as users report and fix
bugs.


How can I help Flake8 release faster?
=====================================

Look at the next milestone. If there's work you can help us complete, that
will help us get to the next milestone. If there's a show-stopping bug that
needs to be released, let us know but please be kind. |Flake8| is developed
and released entirely on volunteer time.


What is the next version of Flake8?
===================================

In general we try to use milestones to indicate this. If the last release
on PyPI is 3.1.5 and you see a milestone for 3.2.0 in GitHub, there's a
good chance that 3.2.0 is the next release.


Why does Flake8 use ranges for its dependencies?
================================================

|Flake8| uses ranges for mccabe, pyflakes, and pycodestyle because each of
those projects tend to add *new* checks in minor releases. It has been an
implicit design goal of |Flake8|'s to make the list of error codes stable in
its own minor releases. That way if you install something from the 2.5
series today, you will not find new checks in the same series in a month
from now when you install it again.

|Flake8|'s dependencies tend to avoid new checks in patch versions which is
why |Flake8| expresses its dependencies roughly as::

    pycodestyle >= 2.0.0, < 2.1.0
    pyflakes >= 0.8.0, != 1.2.0, != 1.2.1, != 1.2.2, < 1.3.0
    mccabe >= 0.5.0, < 0.6.0

This allows those projects to release patch versions that fix bugs and for
|Flake8| users to consume those fixes.


Should I file an issue when a new version of a dependency is available?
=======================================================================

**No.** The current Flake8 core team (of one person) is also
a core developer of pycodestyle, pyflakes, and mccabe. They are aware of
these releases.

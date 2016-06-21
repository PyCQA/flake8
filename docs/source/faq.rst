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
on PyPI is 3.1.5 and you see a milestone for 3.2.0 in GitLab, there's a
good chance that 3.2.0 is the next release.


Why does Flake8 use ranges for its dependencies?
================================================

|Flake8| uses ranges for mccabe, pyflakes, and pycodestyle because each of
those projects tend to add *new* checks between minor releases. |Flake8|
does not restrict you from using patch versions, but |Flake8| likes to
ensure that if you install |Flake8| 2.6.x repeatedly you will not be
surprised at a later time by a new error code suddenly breaking your
linting. Instead, we use minor versions of |Flake8| to add new checks from
dependencies intentionally.

**Please do not file issues to tell the Flake8 team that a new version is
available on PyPI.** The current Flake8 core team (of one person) is also
a core developer of pycodestyle, pyflakes, and mccabe. They are aware of
these releases.

Buildout integration
=====================

In order to use Flake8 inside a buildout, edit your buildout.cfg and add this::

    [buildout]

    parts +=
        ...
        flake8

    [flake8]
    recipe = zc.recipe.egg
    eggs = flake8
           ${buildout:eggs}
    entry-points =
        flake8=flake8.main:main

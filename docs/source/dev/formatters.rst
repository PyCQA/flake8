===========================================
 Developing a Formatting Plugin for Flake8
===========================================

Flake8 added the ability to develop custom formatting plugins in version
3.0.0. Let's write a plugin together:

.. code-block:: python

    from flake8.formatting import base


    class Example(base.BaseFormatter):
        """Flake8's example formatter."""

        pass

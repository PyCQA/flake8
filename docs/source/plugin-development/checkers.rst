.. _checker-plugins:

===============
Checker Plugins
===============

A |Flake8| checker plugin needs to have a registered entry point. This entry
point must reference a callable object.


Declaring the type of plugin
============================

Flake8 uses certain key parameters to determine the kind of plugin this is and
how it needs to call it:

* If it has a parameter called ``tree`` then this plugin is considered to be an
  AST checker plugin. It will be called once per file and it will receive the
  parsed AST of the file as the ``tree`` parameter.  If this entry point
  references a class, then the call will construct an instance of such class,
  and Flake8 will then call the ``run()`` method on the created object to get
  results.
* If the callable has a parameter called ``physical_line`` then whatever the
  entry point references is called for each physical line and the call is
  expected to yield results directly.
* If the callable has a parameter called ``logical_line`` then the callable
  referred to by the entry point will be called from Flake8 with each logical
  line and is expected to yield results.


.. note::
    Class-style plugins are only supported for AST checker (*tree*) plugins.


The Results
===========

Tree plugins
------------

A tree plugins can be a function or a class. If it is a function, it must take
a parameter called ``tree``. If it is a class, then the ``__init__`` method
must take this parameter.

For a class based plugin, the ``run`` method is in charge of yielding results.
For functions, they must deliver results directly.

Flake8 expects the result of running these plugins to be an iterable of tuples,
each of which contain the following:

* An ``int`` with the line number where the issue appears

* An ``int`` with the offset within the line where the issue appears (column)

* A ``str`` with the error message

* The source of the error (typically the name of the plugin). Although this
  field is not used by |Flake8|, it must be present in each tuple


Physical Line plugins
---------------------

A Physical Line plugin must be callable, it must take a parameter called
``physical_line`` and it must return the result of checking the passed physical
line.

Flake8 expects the result of this call to be an iterable of tuples, each
containing the following:

* An ``int`` with the offset within the line where the reported issue appears

* A ``str`` with the error message


Logical Line Plugins
--------------------

A Logical Line plugin must be callable, it must take a parameter called
``logical_line`` and it must return the result of checking the passed logical
line.

Flake8 expects the result of this call to be an iterable of tuples, each
containing the following:

* An ``int`` with the offset within the logical line where the reported issue
  appears

* A ``str`` with the error message

|Flake8| will take care of the conversion from the reported offset on the
logical line to a physical line and physical column pair before it outputs
errors to the user.


Video Tutorial
==============

Here's a tutorial which goes over building an AST checking plugin from scratch:

.. raw:: html

    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; height: auto; margin-bottom: 1em;">
        <iframe src="https://www.youtube.com/embed/ot5Z4KQPBL8" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
    </div>

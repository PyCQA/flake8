.. _plugin-types:

================
Types of Plugins
================

|Flake8| supports two types of plugins:

- **Check Plugins**: Plugins that contribute additional code checks that will
  get reported together with |Flake8|'s default checks. In these, there are
  three different ways these checks can happen:

  * Once per file. Your checker plugin will be called once per file and it will
    receive a parsed AST for the file.

  * Once per physical line.

  * Once per logical line.

- **Report Plugins**: Plugins that receive errors and modify the way these are
  reported. They can take care of formatting, filtering, aggregating, etc.

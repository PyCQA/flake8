"""The logic for Flake8's integration with setuptools."""
import os

import setuptools

from flake8.main import application as app


class Flake8(setuptools.Command):
    """Run Flake8 via setuptools/distutils for registered modules."""

    description = 'Run Flake8 on modules registered in setup.py'
    # NOTE(sigmavirus24): If we populated this with a list of tuples, users
    # could do something like ``python setup.py flake8 --ignore=E123,E234``
    # but we would have to redefine it and we can't define it dynamically.
    # Since I refuse to copy-and-paste the options here or maintain two lists
    # of options, and since this will break when users use plugins that
    # provide command-line options, we are leaving this empty. If users want
    # to configure this command, they can do so through config files.
    user_options = []

    def initialize_options(self):
        """Override this method to initialize our application."""
        pass

    def finalize_options(self):
        """Override this to parse the parameters."""
        pass

    def package_files(self):
        """Collect the files/dirs included in the registered modules."""
        seen_package_directories = ()
        directories = self.distribution.package_dir or {}
        empty_directory_exists = '' in directories
        packages = self.distribution.packages or []
        for package in packages:
            package_directory = package
            if package in directories:
                package_directory = directories[package]
            elif empty_directory_exists:
                package_directory = os.path.join(directories[''],
                                                 package_directory)

            # NOTE(sigmavirus24): Do not collect submodules, e.g.,
            # if we have:
            #  - flake8/
            #  - flake8/plugins/
            # Flake8 only needs ``flake8/`` to be provided. It will
            # recurse on its own.
            if package_directory.startswith(seen_package_directories):
                continue

            seen_package_directories += (package_directory,)
            yield package_directory

    def module_files(self):
        """Collect the files listed as py_modules."""
        modules = self.distribution.py_modules or []
        filename_from = '{0}.py'.format
        for module in modules:
            yield filename_from(module)

    def distribution_files(self):
        """Collect package and module files."""
        for package in self.package_files():
            yield package

        for module in self.module_files():
            yield module

        yield 'setup.py'

    def run(self):
        """Run the Flake8 application."""
        flake8 = app.Application()
        flake8.run(list(self.distribution_files()))
        flake8.exit()


"""
Implementation of the command-line I{flake8} tool.
"""
from flake8.hooks import git_hook, hg_hook  # noqa
from flake8.main import main
from flake8.main import (check_code, check_file, get_parser,  # noqa
                         Flake8Command)  # noqa


if __name__ == '__main__':
    main()

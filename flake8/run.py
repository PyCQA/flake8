
"""
Implementation of the command-line I{flake8} tool.
"""
from flake8.hooks import git_hook, hg_hook                      # noqa
from flake8.main import check_code, check_file, Flake8Command   # noqa
from flake8.main import main


if __name__ == '__main__':
    main()

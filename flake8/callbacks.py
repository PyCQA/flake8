import atexit
import sys


def install_vcs_hook(option, option_str, value, parser):
    # For now, there's no way to affect a change in how pep8 processes
    # options. If no args are provided and there's no config file present,
    # it will error out because no input was provided. To get around this,
    # when we're using --install-hook, we'll say that there were arguments so
    # we can actually attempt to install the hook.
    # See: https://gitlab.com/pycqa/flake8/issues/2 and
    # https://github.com/jcrocholl/pep8/blob/4c5bf00cb613be617c7f48d3b2b82a1c7b895ac1/pep8.py#L1912
    # for more context.
    parser.values.install_hook = True
    parser.rargs.append('.')


def restore_stdout(old_stdout):
    sys.stdout.close()
    sys.stdout = old_stdout


def redirect_stdout(option, option_str, value, parser):
    fd = open(value, 'w')
    old_stdout, sys.stdout = sys.stdout, fd

    atexit.register(restore_stdout, old_stdout)

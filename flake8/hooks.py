# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
import pycodestyle as pep8
import sys
import stat
from subprocess import Popen, PIPE
import shutil
import tempfile
try:
    from configparser import ConfigParser
except ImportError:   # Python 2
    from ConfigParser import ConfigParser

from flake8 import compat
from flake8.engine import get_parser, get_style_guide


def git_hook(complexity=-1, strict=False, ignore=None, lazy=False):
    """This is the function used by the git hook.

    :param int complexity: (optional), any value > 0 enables complexity
        checking with mccabe
    :param bool strict: (optional), if True, this returns the total number of
        errors which will cause the hook to fail
    :param str ignore: (optional), a comma-separated list of errors and
        warnings to ignore
    :param bool lazy: (optional), allows for the instances where you don't add
        the files to the index before running a commit, e.g., git commit -a
    :returns: total number of errors if strict is True, otherwise 0
    """
    gitcmd = "git diff-index --cached --name-only --diff-filter=ACMRTUXB HEAD"
    if lazy:
        # Catch all files, including those not added to the index
        gitcmd = gitcmd.replace('--cached ', '')

    if hasattr(ignore, 'split'):
        ignore = ignore.split(',')

    # Returns the exit code, list of files modified, list of error messages
    _, files_modified, _ = run(gitcmd)

    # We only want to pass ignore and max_complexity if they differ from the
    # defaults so that we don't override a local configuration file
    options = {}
    if ignore:
        options['ignore'] = ignore
    if complexity > -1:
        options['max_complexity'] = complexity

    tmpdir = tempfile.mkdtemp()

    flake8_style = get_style_guide(paths=['.'], **options)
    filepatterns = flake8_style.options.filename

    # Copy staged versions to temporary directory
    files_to_check = []
    try:
        for file_ in files_modified:
            # get the staged version of the file
            gitcmd_getstaged = "git show :%s" % file_
            _, out, _ = run(gitcmd_getstaged, raw_output=True, decode=False)
            # write the staged version to temp dir with its full path to
            # avoid overwriting files with the same name
            dirname, filename = os.path.split(os.path.abspath(file_))
            prefix = os.path.commonprefix([dirname, tmpdir])
            dirname = compat.relpath(dirname, start=prefix)
            dirname = os.path.join(tmpdir, dirname)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            # check_files() only does this check if passed a dir; so we do it
            if ((pep8.filename_match(file_, filepatterns) and
                 not flake8_style.excluded(file_))):

                filename = os.path.join(dirname, filename)
                files_to_check.append(filename)
                # write staged version of file to temporary directory
                with open(filename, "wb") as fh:
                    fh.write(out)

        # Run the checks
        report = flake8_style.check_files(files_to_check)
    # remove temporary directory
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if strict:
        return report.total_errors

    return 0


def hg_hook(ui, repo, **kwargs):
    """This is the function executed directly by Mercurial as part of the
    hook. This is never called directly by the user, so the parameters are
    undocumented. If you would like to learn more about them, please feel free
    to read the official Mercurial documentation.
    """
    complexity = ui.config('flake8', 'complexity', default=-1)
    strict = ui.configbool('flake8', 'strict', default=True)
    ignore = ui.config('flake8', 'ignore', default=None)
    config = ui.config('flake8', 'config', default=None)

    paths = _get_files(repo, **kwargs)

    # We only want to pass ignore and max_complexity if they differ from the
    # defaults so that we don't override a local configuration file
    options = {}
    if ignore:
        options['ignore'] = ignore
    if complexity > -1:
        options['max_complexity'] = complexity

    flake8_style = get_style_guide(config_file=config, paths=['.'],
                                   **options)
    report = flake8_style.check_files(paths)

    if strict:
        return report.total_errors

    return 0


def run(command, raw_output=False, decode=True):
    p = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    # On python 3, subprocess.Popen returns bytes objects which expect
    # endswith to be given a bytes object or a tuple of bytes but not native
    # string objects. This is simply less mysterious than using b'.py' in the
    # endswith method. That should work but might still fail horribly.
    if decode:
        if hasattr(stdout, 'decode'):
            stdout = stdout.decode('utf-8')
        if hasattr(stderr, 'decode'):
            stderr = stderr.decode('utf-8')
    if not raw_output:
        stdout = [line.strip() for line in stdout.splitlines()]
        stderr = [line.strip() for line in stderr.splitlines()]
    return (p.returncode, stdout, stderr)


def _get_files(repo, **kwargs):
    seen = set()
    for rev in range(repo[kwargs['node']], len(repo)):
        for file_ in repo[rev].files():
            file_ = os.path.join(repo.root, file_)
            if file_ in seen or not os.path.exists(file_):
                continue
            seen.add(file_)
            if file_.endswith('.py'):
                yield file_


def find_vcs():
    try:
        _, git_dir, _ = run('git rev-parse --git-dir')
    except OSError:
        pass
    else:
        if git_dir and os.path.isdir(git_dir[0]):
            if not os.path.isdir(os.path.join(git_dir[0], 'hooks')):
                os.mkdir(os.path.join(git_dir[0], 'hooks'))
            return os.path.join(git_dir[0], 'hooks', 'pre-commit')
    try:
        _, hg_dir, _ = run('hg root')
    except OSError:
        pass
    else:
        if hg_dir and os.path.isdir(hg_dir[0]):
            return os.path.join(hg_dir[0], '.hg', 'hgrc')
    return ''


def get_git_config(option, opt_type='', convert_type=True):
    # type can be --bool, --int or an empty string
    _, git_cfg_value, _ = run('git config --get %s %s' % (opt_type, option),
                              raw_output=True)
    git_cfg_value = git_cfg_value.strip()
    if not convert_type:
        return git_cfg_value
    if opt_type == '--bool':
        git_cfg_value = git_cfg_value.lower() == 'true'
    elif git_cfg_value and opt_type == '--int':
        git_cfg_value = int(git_cfg_value)
    return git_cfg_value


_params = {
    'FLAKE8_COMPLEXITY': '--int',
    'FLAKE8_STRICT': '--bool',
    'FLAKE8_IGNORE': '',
    'FLAKE8_LAZY': '--bool',
}


def get_git_param(option, default=''):
    global _params
    opt_type = _params[option]
    param_value = get_git_config(option.lower().replace('_', '.'),
                                 opt_type=opt_type, convert_type=False)
    if param_value == '':
        param_value = os.environ.get(option, default)
    if opt_type == '--bool' and not isinstance(param_value, bool):
        param_value = param_value.lower() == 'true'
    elif param_value and opt_type == '--int':
        param_value = int(param_value)
    return param_value


git_hook_file = """#!/usr/bin/env python
import sys
from flake8.hooks import git_hook, get_git_param

# `get_git_param` will retrieve configuration from your local git config and
# then fall back to using the environment variables that the hook has always
# supported.
# For example, to set the complexity, you'll need to do:
#   git config flake8.complexity 10
COMPLEXITY = get_git_param('FLAKE8_COMPLEXITY', 10)
STRICT = get_git_param('FLAKE8_STRICT', False)
IGNORE = get_git_param('FLAKE8_IGNORE', None)
LAZY = get_git_param('FLAKE8_LAZY', False)

if __name__ == '__main__':
    sys.exit(git_hook(
        complexity=COMPLEXITY,
        strict=STRICT,
        ignore=IGNORE,
        lazy=LAZY,
        ))
"""


def _install_hg_hook(path):
    getenv = os.environ.get
    if not os.path.isfile(path):
        # Make the file so we can avoid IOError's
        open(path, 'w').close()

    c = ConfigParser()
    c.readfp(open(path, 'r'))
    if not c.has_section('hooks'):
        c.add_section('hooks')

    if not c.has_option('hooks', 'commit'):
        c.set('hooks', 'commit', 'python:flake8.hooks.hg_hook')

    if not c.has_option('hooks', 'qrefresh'):
        c.set('hooks', 'qrefresh', 'python:flake8.hooks.hg_hook')

    if not c.has_section('flake8'):
        c.add_section('flake8')

    if not c.has_option('flake8', 'complexity'):
        c.set('flake8', 'complexity', str(getenv('FLAKE8_COMPLEXITY', 10)))

    if not c.has_option('flake8', 'strict'):
        c.set('flake8', 'strict', getenv('FLAKE8_STRICT', False))

    if not c.has_option('flake8', 'ignore'):
        c.set('flake8', 'ignore', getenv('FLAKE8_IGNORE', ''))

    if not c.has_option('flake8', 'lazy'):
        c.set('flake8', 'lazy', getenv('FLAKE8_LAZY', False))

    with open(path, 'w') as fd:
        c.write(fd)


def install_hook():
    vcs = find_vcs()

    if not vcs:
        p = get_parser()[0]
        sys.stderr.write('Error: could not find either a git or mercurial '
                         'directory. Please re-run this in a proper '
                         'repository.\n')
        p.print_help()
        sys.exit(1)

    status = 0
    if 'git' in vcs:
        if os.path.exists(vcs):
            sys.exit('Error: hook already exists (%s)' % vcs)
        with open(vcs, 'w') as fd:
            fd.write(git_hook_file)
        # rwxr--r--
        os.chmod(vcs, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    elif 'hg' in vcs:
        _install_hg_hook(vcs)
    else:
        status = 1

    sys.exit(status)

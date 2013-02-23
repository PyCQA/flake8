# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
import sys
from subprocess import Popen, PIPE
try:
    from configparser import ConfigParser
except ImportError:   # Python 2
    from ConfigParser import ConfigParser

from flake8.engine import get_parser, get_style_guide
from flake8.main import DEFAULT_CONFIG


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
    gitcmd = "git diff-index --cached --name-only HEAD"
    if lazy:
        gitcmd = gitcmd.replace('--cached ', '')

    _, files_modified, _ = run(gitcmd)

    flake8_style = get_style_guide(
        config_file=DEFAULT_CONFIG, ignore=ignore, max_complexity=complexity)
    report = flake8_style.check_files(files_modified)

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
    config = ui.config('flake8', 'config', default=True)
    if config is True:
        config = DEFAULT_CONFIG

    paths = _get_files(repo, **kwargs)

    flake8_style = get_style_guide(
        config_file=config, max_complexity=complexity)
    report = flake8_style.check_files(paths)

    if strict:
        return report.total_errors

    return 0


def run(command):
    p = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    return (p.returncode, [line.strip() for line in stdout.splitlines()],
            [line.strip() for line in stderr.splitlines()])


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
    if os.path.isdir('.git'):
        if not os.path.isdir('.git/hooks'):
            os.mkdir('.git/hooks')
        return '.git/hooks/pre-commit'
    elif os.path.isdir('.hg'):
        return '.hg/hgrc'
    return ''


git_hook_file = """#!/usr/bin/env python
import sys
import os
from flake8.hooks import git_hook

COMPLEXITY = os.getenv('FLAKE8_COMPLEXITY', 10)
STRICT = os.getenv('FLAKE8_STRICT', False)


if __name__ == '__main__':
    sys.exit(git_hook(complexity=COMPLEXITY, strict=STRICT))
"""


def _install_hg_hook(path):
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
        c.set('flake8', 'complexity', str(os.getenv('FLAKE8_COMPLEXITY', 10)))

    if not c.has_option('flake8', 'strict'):
        c.set('flake8', 'strict', os.getenv('FLAKE8_STRICT', False))

    c.write(open(path, 'w+'))


def install_hook():
    vcs = find_vcs()

    if not vcs:
        p = get_parser()
        sys.stderr.write('Error: could not find either a git or mercurial '
                         'directory. Please re-run this in a proper '
                         'repository.')
        p.print_help()
        sys.exit(1)

    status = 0
    if 'git' in vcs:
        with open(vcs, 'w+') as fd:
            fd.write(git_hook_file)
        os.chmod(vcs, 744)
    elif 'hg' in vcs:
        _install_hg_hook(vcs)
    else:
        status = 1

    sys.exit(status)

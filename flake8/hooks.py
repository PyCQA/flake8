import os
import sys
from flake8.util import (_initpep8, pep8style, skip_file, get_parser,
                         ConfigParser)
from subprocess import Popen, PIPE


def git_hook(complexity=-1, strict=False, ignore=None, lazy=False):
    from flake8.main import check_file
    _initpep8()
    if ignore:
        pep8style.options.ignore = ignore

    warnings = 0

    gitcmd = "git diff-index --cached --name-only HEAD"
    if lazy:
        gitcmd = gitcmd.replace('--cached ', '')

    _, files_modified, _ = run(gitcmd)
    for filename in files_modified:
        ext = os.path.splitext(filename)[-1]
        if ext != '.py':
            continue
        if not os.path.exists(filename):
            continue
        warnings += check_file(path=filename, ignore=ignore,
                               complexity=complexity)

    if strict:
        return warnings

    return 0


def hg_hook(ui, repo, **kwargs):
    from flake8.main import check_file
    complexity = ui.config('flake8', 'complexity', default=-1)
    config = ui.config('flake8', 'config', default=True)
    _initpep8(config_file=config)
    warnings = 0

    for file_ in _get_files(repo, **kwargs):
        warnings += check_file(file_, complexity)

    strict = ui.configbool('flake8', 'strict', default=True)

    if strict:
        return warnings

    return 0


def run(command):
    p = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    p.wait()
    return (p.returncode, [line.strip() for line in p.stdout.readlines()],
            [line.strip() for line in p.stderr.readlines()])


def _get_files(repo, **kwargs):
    seen = set()
    for rev in range(repo[kwargs['node']], len(repo)):
        for file_ in repo[rev].files():
            file_ = os.path.join(repo.root, file_)
            if file_ in seen or not os.path.exists(file_):
                continue
            seen.add(file_)
            if not file_.endswith('.py'):
                continue
            if skip_file(file_):
                continue
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

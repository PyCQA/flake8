import os
from flake8.util import _initpep8, pep8style, skip_file
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
    _initpep8()
    complexity = ui.config('flake8', 'complexity', default=-1)
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


"""
Implementation of the command-line I{flake8} tool.
"""
import sys
import os
import _ast
import pep8
import mccabe
import re


checker = __import__('flake8.checker').checker


def check(codeString, filename):
    """
    Check the Python source given by C{codeString} for flakes.

    @param codeString: The Python source to check.
    @type codeString: C{str}

    @param filename: The name of the file the source came from, used to report
        errors.
    @type filename: C{str}

    @return: The number of warnings emitted.
    @rtype: C{int}
    """
    # First, compile into an AST and handle syntax errors.
    try:
        tree = compile(codeString, filename, "exec", _ast.PyCF_ONLY_AST)
    except SyntaxError, value:
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            print >> sys.stderr, "%s: problem decoding source" % (filename, )
        else:
            line = text.splitlines()[-1]

            if offset is not None:
                offset = offset - (len(text) - len(line))

            print >> sys.stderr, '%s:%d: %s' % (filename, lineno, msg)
            print >> sys.stderr, line

            if offset is not None:
                print >> sys.stderr, " " * offset, "^"

        return 1
    else:
        # Okay, it's syntactically valid.  Now check it.
        w = checker.Checker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        valid_warnings = 0

        for warning in w.messages:
            if _noqa(warning):
                continue
            print warning
            valid_warnings += 1

        return valid_warnings


def _noqa(warning):
    # XXX quick dirty hack, just need to keep the line in the warning
    line = open(warning.filename).readlines()[warning.lineno-1]
    return line.strip().lower().endswith('# noqa')


def checkPath(filename):
    """
    Check the given path, printing out any warnings detected.

    @return: the number of warnings printed
    """
    try:
        return check(file(filename, 'U').read() + '\n', filename)
    except IOError, msg:
        print >> sys.stderr, "%s: %s" % (filename, msg.args[1])
        return 1


def check_file(path, complexity=10):
    warnings = checkPath(path)
    warnings += pep8.input_file(path)
    warnings += mccabe.get_module_complexity(path, complexity)
    return warnings


def check_code(code, complexity=10):
    warnings = check(code, '<stdin>')
    warnings += mccabe.get_code_complexity(code, complexity)
    return warnings


_NOQA = re.compile(r'^# flake8: noqa', re.I | re.M)


def skip_file(path):
    """Returns True if this header is found in path

    # flake8: noqa
    """
    f = open(path)
    try:
        content = f.read()
    finally:
        f.close()
    return _NOQA.match(content) is not None


def _get_python_files(paths):
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if not filename.endswith('.py'):
                        continue
                    fullpath = os.path.join(dirpath, filename)
                    if not skip_file(fullpath):
                        yield fullpath

        else:
            if not skip_file(path):
                yield path


def main():
    pep8.process_options()
    warnings = 0
    args = sys.argv[1:]
    if args:
        for path in _get_python_files(args):
            warnings += check_file(path)
    else:
        stdin = sys.stdin.read()
        warnings += check_code(stdin)

    raise SystemExit(warnings > 0)


def _get_files(repo, **kwargs):
    for rev in xrange(repo[kwargs['node']], len(repo)):
        for file_ in repo[rev].files():
            if not file_.endswith('.py'):
                continue
            if skip_file(file_):
                continue
            yield file_


def hg_hook(ui, repo, **kwargs):
    pep8.process_options()
    warnings = 0
    for file_ in _get_files(repo, **kwargs):
        warnings += check_file(file_)

    strict = ui.config('flake8', 'strict')
    if strict is None:
        strict = True

    if strict.lower() in ('1', 'true'):
        return warnings

    return 0

if __name__ == '__main__':
    main()

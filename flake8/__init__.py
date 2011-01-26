
"""
Implementation of the command-line I{flake8} tool.
"""

import sys
import os
import _ast
import pep8

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
    line = open(warning.filename).readlines()[warning.lineno - 1]
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


def main():
    pep8.process_options()

    warnings = 0
    args = sys.argv[1:]
    if args:
        for arg in args:
            if os.path.isdir(arg):
                for dirpath, dirnames, filenames in os.walk(arg):
                    for filename in filenames:
                        if filename.endswith('.py'):
                            fullpath = os.path.join(dirpath, filename)
                            warnings += checkPath(fullpath)
                            warnings += pep8.input_file(fullpath)
            else:
                warnings += checkPath(arg)
                warnings += pep8.input_file(arg)

    else:
        stdin = sys.stdin.read()
        warnings += check(stdin, '<stdin>')

    raise SystemExit(warnings > 0)

def hg_hook(ui, repo, **kwargs):
    pep8.process_options()
    warnings = 0
    files = []
    for rev in xrange(repo[kwargs['node']], len(repo)):
        for file_ in repo[rev].files():
            if file_ not in files:
                files.append(file_)

    for file_ in files:
        warnings += checkPath(file_)
        warnings += pep8.input_file(file_)

    strict = ui.config('flake8', 'strict')
    if strict is None:
        strict = True

    if strict.lower() in ('1', 'true'):
        return warnings

    return 0

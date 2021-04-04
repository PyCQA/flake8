Please read this brief portion of documentation before going any further: http://flake8.pycqa.org/en/latest/internal/contributing.html#filing-a-bug

<!--
*************************************************************************
NOTE: flake8 is a linting framework and does not implement any checks

if you are reporting a problem with a particular check, please track down
the plugin which implements that check.

some common ones:
- F###: https://github.com/pycqa/pyflakes
- E###, W###: https://github.com/pycqa/pycodestyle
*************************************************************************
-->


*Please describe how you installed Flake8*

Example:

```
$ pip install --user flake8
$ brew install flake8
# etc.
```

**Note**: Some *nix distributions patch Flake8 arbitrarily to accommodate incompatible software versions. If you're on one of those distributions, your issue may be closed and you will be asked to open an issue with your distribution package maintainers instead.

*Please provide the exact, unmodified output of `flake8 --bug-report`*

*Please describe the problem or feature*

*If this is a bug report, please explain with examples (and example code) what you expected to happen and what actually happened.*

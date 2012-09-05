@setlocal enableextensions & python -x %~f0 %* & goto :EOF
# -*- mode: python -*-
from flake8.run import main

if __name__ == '__main__':
    main()

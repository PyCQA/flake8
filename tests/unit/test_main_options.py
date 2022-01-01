from flake8.main import options


def test_stage1_arg_parser():
    stage1_parser = options.stage1_arg_parser()
    opts, args = stage1_parser.parse_known_args(
        ["--foo", "--verbose", "src", "setup.py", "--statistics", "--version"]
    )

    assert opts.verbose
    assert args == ["--foo", "src", "setup.py", "--statistics", "--version"]


def test_stage1_arg_parser_ignores_help():
    stage1_parser = options.stage1_arg_parser()
    _, args = stage1_parser.parse_known_args(["--help", "-h"])
    assert args == ["--help", "-h"]

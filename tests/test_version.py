def test_version_in_pyproject():
    import toml

    import artest

    with open("pyproject.toml") as fp:
        proj = toml.load(fp)
    expected_version = proj["tool"]["poetry"]["version"]
    assert artest.__version__ == expected_version


def test_version_in_docstring():
    import artest

    assert f"Version: {artest.__version__}" in artest.__doc__

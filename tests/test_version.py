def test_version():
    import toml

    import artest

    with open("pyproject.toml") as fp:
        proj = toml.load(fp)
    expected_version = proj["tool"]["poetry"]["version"]
    assert artest.__version__ == expected_version

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sorl-thumbnail")
except PackageNotFoundError:
    # package is not installed
    pass

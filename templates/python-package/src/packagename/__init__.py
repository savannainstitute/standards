"""The package: one module per topic; the version comes from the metadata."""

from importlib.metadata import version

__version__ = version("packagename")

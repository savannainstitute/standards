"""Entry points that run a tool with the configuration this package ships.

standards-config NAME prints the path of a shipped configuration file.
standards-ruff and standards-yamllint run those tools with the shipped
configuration and pass every other argument through, which is what the
pre-commit hooks call.
"""

import json
import shutil
import subprocess
import sys
from importlib import resources


def config_path(name):
    """Return the filesystem path of the shipped configuration file."""
    path = resources.files("standards").joinpath("configs", name)
    if not path.is_file():
        raise SystemExit(f"no shipped configuration named {name}")
    return str(path)


def print_config_path(argv=None):
    """Print the path of the named configuration file."""
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        raise SystemExit("usage: standards-config NAME")
    print(config_path(argv[0]))
    return 0


def run_ruff(argv=None):
    """Run ruff check or ruff format with the shipped settings."""
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in ("check", "format"):
        raise SystemExit(
            "usage: standards-ruff check|format [ruff arguments] [files]"
        )
    command = [
        sys.executable,
        "-m",
        "ruff",
        argv[0],
        "--config",
        config_path("ruff.toml"),
        *argv[1:],
    ]
    return subprocess.run(command).returncode


def run_yamllint(argv=None):
    """Run yamllint with the shipped settings."""
    argv = sys.argv[1:] if argv is None else argv
    command = [
        sys.executable,
        "-m",
        "yamllint",
        "-c",
        config_path("yamllint.yaml"),
        *argv,
    ]
    return subprocess.run(command).returncode


def main_ruff():
    """Console script for standards-ruff."""
    sys.exit(run_ruff())


def main_yamllint():
    """Console script for standards-yamllint."""
    sys.exit(run_yamllint())


def main_config():
    """Console script for standards-config."""
    sys.exit(print_config_path())


def main_markdown():
    """Run the pinned formatter using the contributor's Node installation."""
    npx = shutil.which("npx")
    if npx is None:
        raise SystemExit(
            "Install Node.js 24, including npm, then rerun pre-commit."
        )
    with open(config_path("package.json"), encoding="utf-8") as stream:
        version = json.load(stream)["dependencies"]["prettier"]
    command = [
        npx,
        "--yes",
        f"--package=prettier@{version}",
        "prettier",
        "--write",
        "--config",
        config_path("prettierrc.yaml"),
        "--no-editorconfig",
        *sys.argv[1:],
    ]
    sys.exit(subprocess.run(command).returncode)

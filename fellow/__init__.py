from pathlib import Path

import tomli


def _read_version() -> str:
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject.open("rb") as f:
        data = tomli.load(f)
    return data["project"]["version"]


__version__ = _read_version()

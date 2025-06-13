import os
from pathlib import Path
import warnings


def load_secrets(target: str) -> None:
    """Load secrets from a file into os.environ without overwriting existing keys."""
    path = Path(target)
    if not path.exists():
        return

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                warnings.warn(f"Ignoring invalid line in secrets file: {line.strip()}")
                continue
            key, value = stripped.split("=", 1)
            if key not in os.environ:
                os.environ[key] = value


def add_secret(value: str, key: str, target: str) -> None:
    """Add or update a secret in-place, preserving comments and formatting."""
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    updated = False
    prefix = f"{key}="

    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(prefix):
                    lines.append(f"{key}={value}\n")
                    updated = True
                else:
                    lines.append(line)

    if not updated:
        lines.append(f"{key}={value}\n")

    with path.open("w", encoding="utf-8") as f:
        f.writelines(lines)


def remove_secret(key: str, target: str) -> None:
    path = Path(target)
    """Remove a secret by exact key match, preserving comments and formatting."""
    if not path.exists():
        return

    prefix = f"{key}="
    lines = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith(prefix):
                lines.append(line)

    with path.open("w", encoding="utf-8") as f:
        f.writelines(lines)


def clear_secrets(target: str) -> None:
    """Delete all secrets from the file (comments and formatting are lost)."""
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")

from typing import Optional

from fellow.utils.format_message import format_message
from fellow.utils.load_config import Config


def log_message(
    config: Config, name: str, color: int, content: str, language: Optional[str] = None
) -> None:
    if config.log.active:
        with open(config.log.filepath, "a", encoding="utf-8") as f:
            f.write(
                format_message(
                    name=name,
                    color=color,
                    content=content,
                    spoiler=config.log.spoiler,
                    language=language,
                )
            )


def clear_log(config: Config) -> None:
    if config.log.active:
        with open(config.log.filepath, "w", encoding="utf-8") as f:
            f.write("")

from typing import Optional

from fellow.utils.format_message import format_message


def log_message(config, name, color, content, language: Optional[str] = None):
    if config.get("log"):
        with open(config["log"], "a", encoding="utf-8") as f:
            f.write(
                format_message(
                    name=name,
                    color=color,
                    content=content,
                    language=language,
                )
            )


def clear_log(config):
    if config.get("log"):
        with open(config["log"], "w", encoding="utf-8") as f:
            f.write("")

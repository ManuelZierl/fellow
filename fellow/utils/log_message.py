from fellow.utils.format_message import format_message


def log_message(config, name, color, content, language="txt"):
    if config.get("log"):
        with open(config["log"], "a", encoding="utf-8") as f:
            f.write(format_message(name=name, color=color, content=content, language=language))

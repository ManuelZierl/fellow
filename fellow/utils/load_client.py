from pathlib import Path
from typing import Optional, Type, cast

from fellow.clients import ALL_CLIENTS
from fellow.clients.Client import Client, ClientConfig
from fellow.utils.load_config import Config
from fellow.utils.load_python_module import load_python_module


def load_client(system_content: str, config: Config) -> Client:
    client_name = config.ai_client.client
    for path_str in config.custom_clients_paths:
        path = Path(path_str).resolve()
        if not path.exists() or not path.is_dir():
            print(f"[WARNING] Skipping {path_str}: not a valid directory.")
            continue

        for file in path.glob("*.py"):
            name: str = file.stem.lower()
            if not name.endswith("client"):
                continue
            name = name[: -len("client")]
            if not client_name == name:
                continue

            module = load_python_module(file)
            client_class: Optional[Type[Client]] = cast(
                Optional[Type[Client]], getattr(module, file.stem, None)
            )
            if client_class is None:
                print(f"[WARNING] Skipping {file.name}: `client_class` is None.")
                continue
            # todo: check if client_class is a subclass of Client that implements the protocol correctly
            client_config_class: Type[ClientConfig] = client_class.config_class
            client_config = client_config_class(
                system_content=system_content, **(config.ai_client.config or {})
            )

            return client_class.create(client_config)

    client_class = ALL_CLIENTS.get(client_name)
    if client_class:
        client_config_class = client_class.config_class
        client_config = client_config_class(
            system_content=system_content, **(config.ai_client.config or {})
        )
        return client_class.create(client_config)

    raise ValueError(f"[ERROR] Client '{client_name}' not found")

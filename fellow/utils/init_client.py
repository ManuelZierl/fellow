from pathlib import Path

CLIENT_TEMPLATE = """\
from typing import List, Optional

from typing_extensions import Self

from fellow.clients.Client import (
    ChatResult,
    Client,
    ClientConfig,
    Function,
    FunctionResult,
)


class {{client_name}}ClientConfig(ClientConfig):
    system_content: str
    # todo:


class {{client_name}}Client(Client[{{client_name}}ClientConfig]):
    config_class = {{client_name}}ClientConfig

    def __init__(self, config: {{client_name}}ClientConfig):
        # todo:
        ...

    @classmethod
    def create(cls, config: {{client_name}}ClientConfig) -> Self:
        return cls(config)

    def chat(
        self,
        functions: List[Function],
        message: str = "",
        function_result: Optional[FunctionResult] = None,
    ) -> ChatResult:
        # todo:

        return ChatResult(
            message=...,
            function_name=...,
            function_args=...,
        )

    def store_memory(self, filename: str) -> None:
        # todo:
        ...

"""


def init_client(client_name: str, target: str) -> Path:
    """
    todo: doc
    todo: test
    """
    target_dir = Path(target)
    client_name = client_name.lower().capitalize()
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / f"{client_name}Client.py"

    if file_path.exists():
        raise FileExistsError(f"Client file already exists: {file_path}")

    content = CLIENT_TEMPLATE.format(
        client_name=client_name,
    )

    file_path.write_text(content)
    return file_path

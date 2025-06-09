from pathlib import Path

POLICY_TEMPLATE = """\
from typing import TYPE_CHECKING, List, Union
from pydantic import Field

from fellow.policies.Policy import Policy, PolicyConfig

if TYPE_CHECKING:
    from fellow.commands.Command import CommandContext, CommandHandler, CommandInput


class {config_class_name}(PolicyConfig):
    # TODO: Define your configuration fields here
    example_field: List[str] = Field(
        default_factory=list,
        description="Example config field for the policy."
    )


class {policy_class_name}(Policy[{config_class_name}]):
    \"\"\"
    Brief description of what this policy does.
    \"\"\"

    def __init__(self, config: {config_class_name}):
        self.config = config

    def check(
        self,
        command_name: str,
        command_handler: "CommandHandler",
        args: "CommandInput",
        context: "CommandContext",
    ) -> Union[bool, str]:
        # TODO: Implement policy logic here
        return True
"""


def init_policy(policy_name: str, target: str) -> Path:
    """
    Generates a boilerplate file for a custom policy.
    For example, `deny_large_file` creates:
    - Class: DenyLargeFileConfig
    - Class: DenyLargeFile
    - File: deny_large_file.py

    :param policy_name: The name of the policy, typically in snake_case.
    :param target: The directory where the policy file should be created.
    :return: The path to the created policy file.
    """
    target_dir = Path(target)
    target_dir.mkdir(parents=True, exist_ok=True)

    parts = policy_name.split("_")
    class_base = "".join(part.capitalize() for part in parts)
    policy_class_name = class_base
    config_class_name = f"{class_base}Config"
    file_path = target_dir / f"{policy_name}.py"

    if file_path.exists():
        raise FileExistsError(f"Policy file already exists: {file_path}")

    content = POLICY_TEMPLATE.format(
        policy_class_name=policy_class_name,
        config_class_name=config_class_name,
    )

    file_path.write_text(content)
    return file_path

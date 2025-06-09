import fnmatch
import os
from typing import TYPE_CHECKING, List, Union

from pydantic import Field

from fellow.policies.Policy import Policy, PolicyConfig

if TYPE_CHECKING:
    from fellow.commands.Command import (  # pragma: no cover
        CommandContext,
        CommandHandler,
        CommandInput,
    )


class DenyIfFieldInBlacklistConfig(PolicyConfig):
    fields: List[str] = Field(
        ["filename"],
        description="Fields of the CommandInput to check against the blacklist",
    )
    blacklist: List[str] = Field(
        default=[],
        description="Patterns to block",
    )


class DenyIfFieldInBlacklist(Policy[DenyIfFieldInBlacklistConfig]):
    """
    Policy that denies commands if any specified field in the CommandInput matches a pattern in the blacklist.
    """

    def __init__(self, config: DenyIfFieldInBlacklistConfig):
        self.config = config

    def check(
        self,
        command_name: str,
        command_handler: "CommandHandler",
        args: "CommandInput",
        context: "CommandContext",
    ) -> Union[bool, str]:
        for field in self.config.fields:
            value = getattr(args, field, None)
            if not isinstance(value, str):
                continue

            normalized = value.replace(os.sep, "/")

            for pattern in self.config.blacklist:
                if fnmatch.fnmatch(normalized, pattern):
                    return (
                        f"Denied by pattern '{pattern}' on field '{field}': '{value}'"
                    )
        return True

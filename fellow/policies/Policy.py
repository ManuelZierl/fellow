from typing import TYPE_CHECKING, Protocol, TypeVar, Union

from pydantic import BaseModel

if TYPE_CHECKING:
    from fellow.commands import CommandHandler  # pragma: no cover
    from fellow.commands.Command import CommandContext, CommandInput  # pragma: no cover


class PolicyConfig(BaseModel):
    """
    Base class for any policy config. Concrete policies should subclass this
    and define their fields explicitly.
    """

    ...


T = TypeVar("T", bound=PolicyConfig, covariant=True)


class Policy(Protocol[T]):
    """
    A policy defines a check before a command is executed.
    If it returns True, execution is allowed.
    If it returns a string, it is treated as a denial reason.
    """

    def __init__(self, config: T): ...

    def check(
        self,
        command_name: str,
        command_handler: "CommandHandler",
        args: "CommandInput",
        context: "CommandContext",
    ) -> Union[bool, str]: ...

from typing import TYPE_CHECKING, Union

from pydantic import Field

from fellow.policies.Policy import Policy, PolicyConfig

if TYPE_CHECKING:
    from fellow.commands.Command import CommandContext, CommandHandler, CommandInput


class RequireUserConfirmationConfig(PolicyConfig):
    message: str = Field(
        "Fellow wants to run '{command_name}' command with args {args}. Please confirm by typing 'y' or 'yes' to proceed: ",
        description="Confirmation message to present to the user before running the command",
    )


class RequireUserConfirmation(Policy[RequireUserConfirmationConfig]):
    """
    Policy that asks the user for confirmation before allowing the command to proceed.
    """

    def __init__(self, config: RequireUserConfirmationConfig):
        self.config = config

    def check(
        self,
        command_name: str,
        command_handler: "CommandHandler",
        args: "CommandInput",
        context: "CommandContext",
    ) -> Union[bool, str]:
        message = self.config.message.format(command_name=command_name, args=args)
        try:
            answer = input(message)
        except EOFError:
            return "[DENIED] No input available to confirm action."

        if answer in ("y", "yes"):
            return True
        return f"[DENIED] User denied this command with the response: '{answer}'."

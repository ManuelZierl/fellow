from fellow.commands.command import CommandContext, CommandHandler, CommandInput


class CommandClient:
    def __init__(self, context: CommandContext):
        """
        Initializes the CommandClient with a dictionary of commands.
        :param context: The context in which the command will be executed, typically containing the AI client.
        """
        self.context = context

    def run(self, args: CommandInput, handler_fn: CommandHandler) -> str:
        """
        Run a structured command given as a JSON string with one top-level key.
        """
        try:
            return handler_fn(args, context=self.context)
        except Exception as e:
            return f"[ERROR] Command execution failed: {e}"

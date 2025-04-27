from pydantic import Field

from fellow.commands import CommandInput
from fellow.commands.Command import CommandContext


class MakePlanInput(CommandInput):
    plan: str = Field(..., description="The plan made by the AI")


def make_plan(args: MakePlanInput, context: CommandContext) -> str:
    """
    Creates a plan for the AI to follow. The plan will be in every future message for guidance.
    """
    context["ai_client"].set_plan(args.plan)
    return "[OK] Plan created"

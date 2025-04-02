from pydantic import Field

from fellow.commands import CommandInput
from fellow.commands.command import CommandContext


class MakePlanInput(CommandInput):
    plan: str = Field(..., description="The plan made by the AI")


def make_plan(args: MakePlanInput, context: CommandContext) -> str:
    """
    Creates a plan for the AI to follow. The plan will be in every future message for guidance.
    """
    context.ai_client.system_content.append(
        {
            "role": "system",
            "content": args.plan,
            "tokens": context.ai_client.count_tokens({"role": "system", "content": args.plan})
        }
    )
    return "[OK] Plan created"
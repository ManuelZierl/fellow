import pytest

from fellow.commands import CommandInput
from fellow.commands.Command import Command
from fellow.policies import Policy


def test_invalid_policy_raises():
    class InvalidPolicy(Policy):
        def check(self, *args, **kwargs):
            return 1  # not a string

    class DummyCommandInput(CommandInput):
        pass

    def dummy_handler(args: DummyCommandInput, context):
        return "dummy response"

    command = Command(DummyCommandInput, dummy_handler, [InvalidPolicy])
    with pytest.raises(ValueError) as e:
        command.run("{}", None)
    assert (
        str(e.value)
        == "[ERROR] Policy check did not return True but did not give a denial reason."
    )

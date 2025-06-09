from unittest.mock import patch

import pytest

from fellow.policies.RequireUserConfirmation import (
    RequireUserConfirmation,
    RequireUserConfirmationConfig,
)


class DummyArgs:
    def __repr__(self):
        return "DummyArgs(x=1)"


class DummyContext:
    pass


class DummyHandler:
    __name__ = "dummy_handler"


@pytest.mark.parametrize("user_input", ["y", "yes"])
def test_confirmation_accepted(user_input):
    policy = RequireUserConfirmation(RequireUserConfirmationConfig(message="Proceed?"))
    with patch("builtins.input", return_value=user_input):
        result = policy.check(
            "dummy_command", DummyHandler(), DummyArgs(), DummyContext()
        )
        assert result is True


@pytest.mark.parametrize("user_input", ["n", "no", "abc", "", "YEAH"])
def test_confirmation_denied(user_input):
    policy = RequireUserConfirmation(RequireUserConfirmationConfig(message="Proceed?"))
    with patch("builtins.input", return_value=user_input):
        result = policy.check(
            "dummy_command", DummyHandler(), DummyArgs(), DummyContext()
        )
        assert isinstance(result, str)
        assert "[DENIED]" in result


def test_confirmation_eoferror():
    policy = RequireUserConfirmation(RequireUserConfirmationConfig(message="Proceed?"))
    with patch("builtins.input", side_effect=EOFError):
        result = policy.check(
            "dummy_command", DummyHandler(), DummyArgs(), DummyContext()
        )
        assert result == "[DENIED] No input available to confirm action."

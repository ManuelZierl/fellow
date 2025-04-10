import sys

import pytest

from fellow.utils.parse_args import parse_args, str2bool


def test_str2bool_true_values():
    true_values = ["yes", "true", "t", "1", "TRUE", "Yes"]
    for val in true_values:
        assert str2bool(val) is True


def test_str2bool_false_values():
    false_values = ["no", "false", "f", "0", "", "random"]
    for val in false_values:
        assert str2bool(val) is False


@pytest.mark.parametrize(
    "cli_args, expected",
    [
        (["--task", "Build something"], {"task": "Build something"}),
        (["--log.filepath", "test.md"], {"log.filepath": "test.md"}),
        (["--log.active", "true"], {"log.active": True}),
        (["--log.active", "false"], {"log.active": False}),
        (
            ["--openai_config.memory_max_tokens", "1234"],
            {"openai_config.memory_max_tokens": 1234},
        ),
        (["--commands", "run", "test"], {"commands": ["run", "test"]}),
    ],
)
def test_parse_args(monkeypatch, cli_args, expected):
    monkeypatch.setattr(sys, "argv", ["cli"] + cli_args)
    args = parse_args()
    print(args)
    for key, value in expected.items():
        assert getattr(args, key) == value

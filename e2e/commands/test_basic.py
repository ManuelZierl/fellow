import os
from pathlib import Path

from e2e.utils import run_command


def test_fellow_init_command(setup_env, tmp_path):
    os.chdir(tmp_path)

    result = run_command("fellow init-command do_something")
    expected_path = Path(".fellow") / "commands" / "do_something.py"
    assert result == f"[OK] Command file created: {expected_path}"

    assert expected_path.exists(), f"Expected file not found: {expected_path}"

    content = (tmp_path / expected_path).read_text()
    assert "class DoSomethingInput(CommandInput):" in content
    assert (
        "def do_something(args: DoSomethingInput, context: CommandContext) -> str:"
        in content
    )

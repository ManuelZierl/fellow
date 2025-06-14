import os

from e2e.utils import run_command


def test_fellow_init_command(setup_env, tmp_path):
    os.chdir(tmp_path)

    result = run_command("fellow init-command do_something")
    assert result == "[OK] Command file created: .fellow/commands/do_something.py"

    path = tmp_path / ".fellow" / "commands" / "do_something.py"
    assert path.exists(), f"Expected file not found: {path}"

    content = path.read_text()
    assert "class DoSomethingInput(CommandInput):" in content
    assert (
        "def do_something(args: DoSomethingInput, context: CommandContext) -> str:"
        in content
    )

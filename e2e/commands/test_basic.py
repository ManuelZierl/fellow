import os
import re
from pathlib import Path

from e2e.utils import run_command


def test_fellow_init_command(tmp_path):
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


def test_fellow_init_client(tmp_path):
    os.chdir(tmp_path)

    result = run_command("fellow init-client my")
    expected_path = Path(".fellow") / "clients" / "MyClient.py"
    assert result == f"[OK] Client file created: {expected_path}"
    assert expected_path.exists()

    content = (tmp_path / expected_path).read_text()
    assert "MyClientConfig(ClientConfig)" in content
    assert "class MyClient(Client[MyClientConfig])" in content


def test_fellow_init_policy(tmp_path):
    os.chdir(tmp_path)

    result = run_command("fellow init-policy dont_do_this")
    expected_path = Path(".fellow") / "policies" / "dont_do_this.py"
    assert result == f"[OK] Policy file created: {expected_path}"
    assert expected_path.exists()

    content = (tmp_path / expected_path).read_text()
    assert "class DontDoThisConfig(PolicyConfig):" in content
    assert "class DontDoThis(Policy[DontDoThisConfig]):" in content


def test_fellow_add_remove_clear_secret(tmp_path):
    os.chdir(tmp_path)

    # Add secret
    result_add = run_command("fellow add-secret TEST_SECRET test123")
    assert "[OK] Secret added: TEST_SECRET" in result_add
    secrets_file = Path(".fellow") / ".secrets"
    assert secrets_file.exists()
    assert "TEST_SECRET=test123" in secrets_file.read_text()

    # Remove secret
    result_remove = run_command("fellow remove-secret TEST_SECRET")
    assert "[OK] Secret removed: TEST_SECRET" in result_remove
    assert "TEST_SECRET" not in secrets_file.read_text()

    # Add another and then clear
    run_command("fellow add-secret ANOTHER_SECRET value")
    result_clear = run_command("fellow clear-secrets")
    assert "[OK] All secrets cleared." in result_clear
    assert secrets_file.read_text().strip() == ""


def test_fellow_help():
    result = run_command("fellow --help")
    assert "usage:" in result.lower()
    assert "init-command" in result
    assert "add-secret" in result


def test_fellow_version():
    result = run_command("fellow --version")
    assert re.match(r"fellow \d+\.\d+\.\d+", result)

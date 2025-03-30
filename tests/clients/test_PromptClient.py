from fellow.clients.PromptClient import PromptClient


def test_echo_simple():
    sh = PromptClient()
    result = sh.run("echo hello")
    assert result == "hello"

def test_multiple_runs():
    sh = PromptClient()
    a = sh.run("echo first")
    b = sh.run("echo second")
    assert a == "first"
    assert b == "second"

def test_command_with_tab_output():
    sh = PromptClient()
    result = sh.run("echo -e 'a\\tb'")
    assert result == "a\tb"

def test_command_fails_gracefully():
    sh = PromptClient()
    result = sh.run("someunknowncommand")
    assert "command not found" in result or "not recognized" in result.lower()


import importlib
from unittest.mock import MagicMock

import pytest

# dynamischer Import, um Patch-Probleme zu umgehen
summarize_module = importlib.import_module("fellow.commands.summarize_file")
SummarizeFileInput = summarize_module.SummarizeFileInput
summarize_file = summarize_module.summarize_file


def test_file_not_found():
    args = SummarizeFileInput(filepath="non_existent.txt")
    context = MagicMock(ai_client=MagicMock(model="gpt-4"))
    result = summarize_file(args, context)
    assert "[ERROR] File not found" in result


def test_empty_file(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   ")  # only whitespace

    args = SummarizeFileInput(filepath=str(file_path))
    context = MagicMock(ai_client=MagicMock(model="gpt-4"))
    result = summarize_file(args, context)
    assert result == "[INFO] File is empty or only contains whitespace."


def test_summary_output(tmp_path):
    file_path = tmp_path / "example.txt"
    file_path.write_text("Dies ist ein Testinhalt.")

    mock_client = MagicMock()
    # Adjust to return a tuple as expected by chat()
    mock_client.chat.return_value = ("Das ist eine Zusammenfassung.", None, None)

    summarize_module.OpenAIClient = lambda **kwargs: mock_client

    args = SummarizeFileInput(filepath=str(file_path))
    context = MagicMock(ai_client=MagicMock(model="gpt-4"))
    result = summarize_file(args, context)

    assert result == "[OK] Summary:\nDas ist eine Zusammenfassung."
    mock_client.chat.assert_called_once()


def test_file_read_error(tmp_path):
    file_path = tmp_path / "protected.txt"
    file_path.write_text("Zugriff verweigert")
    file_path.chmod(0o000)  # keine Berechtigung zum Lesen

    args = SummarizeFileInput(filepath=str(file_path))
    context = MagicMock(ai_client=MagicMock(model="gpt-4"))

    try:
        result = summarize_file(args, context)
    finally:
        file_path.chmod(0o644)  # Berechtigung wiederherstellen, sonst cleanup failt

    assert "[ERROR] Could not read or summarize file" in result


def test_max_chars_truncates(tmp_path):
    file_path = tmp_path / "long.txt"
    file_path.write_text("A" * 1000)

    mock_client = MagicMock()
    # Adjust to return a tuple as expected by chat()
    mock_client.chat.return_value = ("Zusammenfassung für 100 Zeichen.", None, None)

    summarize_module.OpenAIClient = lambda **kwargs: mock_client

    args = SummarizeFileInput(filepath=str(file_path), max_chars=100)
    context = MagicMock(ai_client=MagicMock(model="gpt-4"))
    result = summarize_file(args, context)

    assert "[OK] Summary:\nZusammenfassung für 100 Zeichen." == result
    call_arg = mock_client.chat.call_args[0][0]
    assert len(call_arg) < 200  # sollte etwa 100 + prompt sein

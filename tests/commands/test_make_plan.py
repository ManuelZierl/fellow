from unittest.mock import MagicMock

from fellow.clients.OpenAIClient import OpenAIClient
from fellow.commands.command import CommandContext
from fellow.commands.make_plan import MakePlanInput, make_plan


# Fake client that is Pydantic-compliant but internally mocked
class FakeOpenAIClient(OpenAIClient):
    def __init__(self):
        self.system_content = []
        self.count_tokens = MagicMock(return_value=42)


def test_make_plan_appends_to_system_content():
    # Arrange
    plan_text = "First, load data. Then preprocess it. Finally, train the model."
    input_data = MakePlanInput(plan=plan_text)
    fake_client = FakeOpenAIClient()
    context = CommandContext(ai_client=fake_client)

    # Act
    result = make_plan(input_data, context)

    # Assert
    assert result == "[OK] Plan created"
    assert len(fake_client.system_content) == 1
    content_entry = fake_client.system_content[0]
    assert content_entry["role"] == "system"
    assert content_entry["content"] == plan_text
    assert content_entry["tokens"] == 42
    fake_client.count_tokens.assert_called_once_with(
        {"role": "system", "content": plan_text}
    )

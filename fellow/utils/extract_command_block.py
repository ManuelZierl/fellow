import json
from typing import Tuple


def find_action_start_and_end(response: str) -> Tuple[int, int] | str:
    """
    Finds the start and end indices of the JSON block in the response string.
    :param response: The response string containing the JSON block.
    :return: tuple of start and end indices of the JSON block, or an error message if the block is malformed.
    """
    action_start = response.find("Action:")
    if action_start == -1:
        return "[ERROR] No Action: block found in response"

    json_start = response.find("{", action_start)
    if json_start == -1:
        return "[ERROR] No JSON opening brace found after Action:"

    brace_count = 0
    json_end = json_start

    for i in range(json_start, len(response)):
        if response[i] == "{":
            brace_count += 1
        elif response[i] == "}":
            brace_count -= 1

        if brace_count == 0:
            json_end = i
            break

    if brace_count != 0:
        return "[ERROR] JSON block braces do not match."
    return json_start, json_end + 1


def extract_command_block(response: str) -> dict | str:
    """
    Extracts the JSON command block from a response string. If the JSON block is malformed or if the Action block is
    missing, it returns None.
    :param response:
    :return: the extracted JSON command block as a dictionary or None if extraction fails.
    """
    action_start_and_end = find_action_start_and_end(response)
    if isinstance(action_start_and_end, str):
        return action_start_and_end
    json_start, json_end = action_start_and_end
    json_block = response[json_start:json_end+1]
    return json.loads(json_block)
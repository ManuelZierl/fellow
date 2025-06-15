import json
import platform
import subprocess


def run_command(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
    assert result.returncode == 0, f"Command failed: {cmd}"
    return result.stdout.strip()


def json_to_command_line_string(data: dict) -> str:
    json_arg = json.dumps(data)
    if platform.system() == "Windows":
        json_arg = json_arg.replace('"', '\\"')
        return f'"{json_arg}"'
    if platform.system() in {"Darwin", "Linux"}:
        return f"'{json_arg}'"
    return json_arg

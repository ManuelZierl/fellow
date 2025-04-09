import subprocess
from unittest.mock import patch

import pytest

from fellow.commands.pip_install import PipInstallInput, pip_install


@patch("subprocess.run")
def test_pip_install_success(mock_run):
    # Mock subprocess.run to simulate successful pip install
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "Successfully installed package."

    result = pip_install(PipInstallInput(package_name="numpy"), None)

    assert result == "Successfully installed package."
    mock_run.assert_called_once()
    assert mock_run.call_args.args[0][0].endswith("python")
    assert mock_run.call_args.args[0][1:] == ["-m", "pip", "install", "numpy"]


@patch("subprocess.run")
def test_pip_install_version_success(mock_run):
    # Mock subprocess.run to simulate successful pip install with version
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "Successfully installed package."

    result = pip_install(PipInstallInput(package_name="numpy", version="1.19.2"), None)

    assert result == "Successfully installed package."
    mock_run.assert_called_once()
    assert mock_run.call_args.args[0][0].endswith("python")
    assert mock_run.call_args.args[0][1:] == ["-m", "pip", "install", "numpy==1.19.2"]


@patch("subprocess.run")
def test_pip_install_failure(mock_run):
    # Mock subprocess.run to simulate a failure in pip install
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="pip install numpy", stderr="ERROR: Package not found."
    )

    result = pip_install(PipInstallInput(package_name="nonexistentpackage"), None)

    assert (
        result
        == "Failed to install nonexistentpackage. Error: ERROR: Package not found."
    )


@patch("subprocess.run")
def test_pip_install_unexpected_exception(mock_run):
    # Mock subprocess.run to simulate an unexpected exception
    mock_run.side_effect = Exception("Unexpected error")

    result = pip_install(PipInstallInput(package_name="numpy"), None)

    assert result == "An unexpected error occurred: Unexpected error"

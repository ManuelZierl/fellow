[![Version](https://img.shields.io/pypi/v/fellow.svg)](https://pypi.org/project/fellow/)
![CI](https://github.com/ManuelZierl/fellow/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/ManuelZierl/fellow/branch/main/graph/badge.svg)](https://codecov.io/gh/ManuelZierl/fellow)


<table border="0" style="border: none; border-collapse: collapse;">
  <tr>
    <td style="border: none; padding: 0 8px 0 0; vertical-align: middle;">
      <img src="img/logo.svg" width="40" height="40" alt="Fellow Logo">
    </td>
    <td style="border: none; vertical-align: middle;">
      <span style="font-size: 2em;"><strong>Fellow</strong></span>
    </td>
  </tr>
</table>

## Project Description
**Fellow** is a command-line interface (CLI) tool that acts as an autonomous software engineering assistant. It uses the OpenAI API to perform various structured tasks by reasoning step-by-step, executing commands, and maintaining a log of its activities.

---

## Installation
Make sure you have Python installed on your system. Then install Fellow via [pip](https://pypi.org/project/fellow/):
```bash
pip install fellow
```

## Usage
Since Fellow uses the OpenAI API you have to set your `OPENAI_API_KEY` in your environment variables. You can do this by running:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

Fellow is designed to run based on a configuration provided via a YAML file. A typical usage example:
```bash
fellow --config task.yml
```

In the YAML configuration, you can specify tasks that Fellow will carry out. Supported commands include file operations, code execution, and more. Example:
```yaml
task: |
  write a readme file for this Python project
``` 
For more configuration options, see the [default_fellow_config.yml](fellow/default_fellow_config.yml) file in the repository.

## Contributing
We welcome contributions! Please fork the repository and submit a pull request.

## Licensing
This project is licensed under the MIT License.
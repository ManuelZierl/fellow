[![Version](https://img.shields.io/pypi/v/fellow.svg)](https://pypi.org/project/fellow/)
![CI](https://github.com/ManuelZierl/fellow/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/ManuelZierl/fellow/branch/main/graph/badge.svg)](https://codecov.io/gh/ManuelZierl/fellow)
# Fellow

## Project Description
Fellow is a command-line interface (CLI) tool designed to act as an autonomous senior software engineering assistant. It interfaces with the OpenAI API to perform various structured tasks by reasoning step-by-step, executing commands, and maintaining a log of activities.

## Installation Instructions
To install Fellow, ensure you have Python installed on your system, then use pip to install:
```bash
pip install fellow
```

## Usage
Fellow operates on a configuration provided via a YAML file. An example of running the fellow command is:
```bash
fellow --config task.yml
```
You can specify tasks and configurations that Fellow will execute. The commands supported include file operations, code execution, and more. For example:
```yaml
task: |
  write a readme file for this Python project
``` 
for more configurations, refer to the [default_fellow_config.yml](fellow/default_fellow_config.yml) file in the repository.

## Contributing
We welcome contributions! Please fork the repository and submit a pull request.

## Licensing
This project is licensed under the MIT License.
[![Version](https://img.shields.io/pypi/v/fellow?color=blue&logo=pypi)](https://pypi.org/project/fellow/)
![CI](https://github.com/ManuelZierl/fellow/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/ManuelZierl/fellow/branch/main/graph/badge.svg)](https://codecov.io/gh/ManuelZierl/fellow)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![PyPI - Types](https://img.shields.io/pypi/types/fellow)
![GitHub License](https://img.shields.io/github/license/ManuelZierl/fellow)


# ![Fellow](https://raw.githubusercontent.com/ManuelZierl/fellow/main/docs/img/logo.svg)

## Project Description
**Fellow** is a command-line AI assistant built by developers, for developers.

Unlike most AI tools that stop at suggesting code, **Fellow** goes a step further: it executes tasks on your behalf. It reasons step-by-step, chooses appropriate commands from a plugin system, and performs actions like editing files, generating content, or writing tests. All autonomously.

The idea for Fellow started from a simple but powerful realization: *copy-pasting between ChatGPT and your editor gets in the way of real flow.* What if the AI could access your codebase directly? What if it could decide *what to look at* and *what to do*—without constant human prompting?

That's what Fellow explores. It uses YAML configs to define tasks, keeps a memory of its reasoning, and can be extended with your own command plugins. Whether you're automating repetitive dev tasks or experimenting with agentic workflows, Fellow is a lightweight but powerful sandbox for building the tools you wish existed.

It’s still early and evolving—but it already works. And if you're a developer who wants more *doing* and less *prompting*, Fellow might just be the tool you've been waiting for.

## Documentation

Full documentation for **Fellow** is available at: [Documentation](https://manuelzierl.github.io/fellow)

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

## Customization

Fellow is built to be extensible. You can customize both:

- **Commands** – add your own automation logic or override existing ones. Learn more in the [Custom Commands documentation](https://manuelzierl.github.io/fellow/commands/custom)

- **Clients** – integrate with different AI backends like built-in OpenAI or Gemini. Or create your own client. Learn more in the [Custom Clients documentation](https://manuelzierl.github.io/fellow/clients/custom)

---

## Changelog
All notable changes to this project will be documented in this file: [CHANGELOG.md](CHANGELOG.md)

---

## Contributing
We welcome contributions! Please fork the repository and submit a pull request.

---

## Licensing
This project is licensed under the MIT License.
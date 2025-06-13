[![Version](https://img.shields.io/pypi/v/fellow?color=blue&logo=pypi)](https://pypi.org/project/fellow/)
![CI](https://github.com/ManuelZierl/fellow/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/ManuelZierl/fellow/branch/main/graph/badge.svg)](https://codecov.io/gh/ManuelZierl/fellow)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![PyPI - Types](https://img.shields.io/pypi/types/fellow)
![GitHub License](https://img.shields.io/github/license/ManuelZierl/fellow)


# ![Fellow](https://raw.githubusercontent.com/ManuelZierl/fellow/main/docs/assets/img/logo.svg)

## Project Description

**Fellow** is a command-line AI assistant built by developers, for developers.

Unlike most AI tools that just suggest code, **Fellow** goes further: it *executes* tasks for you. It reasons step-by-step, picks commands from a plugin system, and performs actions like editing files, generating content, or writing tests — all autonomously.

Fellow was born from a simple insight: *copy-pasting between ChatGPT and your editor breaks flow.* What if the AI could access your codebase directly and decide what to do?

It’s a lightweight but powerful sandbox for building the tools you wish existed — and it's still evolving. If you're a developer who wants more *doing* and less *prompting*, Fellow might just be the tool you’ve been waiting for.

## Documentation

Full documentation for **Fellow** is available at: [Documentation](https://manuelzierl.github.io/fellow)

---

## Installation
Make sure you have Python installed on your system. Then install Fellow via [pip](https://pypi.org/project/fellow/):
```bash
pip install fellow
```

## Quick Start

Fellow can use the OpenAI API, so you need to provide your API key. The easiest way is:

```bash
fellow add-secret OPENAI_API_KEY your_openai_api_key
```

Then you're ready to go. For example, to ask Fellow to write a README file:

```bash
fellow --task "write a readme file for this Python project"
```

---


## Customization

Fellow is built to be extensible. You can customize:

- **Commands** – add your own automation logic or override existing ones. Learn more in the [Custom Commands documentation](https://manuelzierl.github.io/fellow/commands/custom)

- **Clients** – integrate with different AI backends like built-in OpenAI or Gemini. Or create your own client. Learn more in the [Custom Clients documentation](https://manuelzierl.github.io/fellow/clients/custom)

- **Policies** – control Fellow’s behavior in specific situations to ensure safe and predictable AI use. [Custom Policies documentation](https://manuelzierl.github.io/fellow/policies/custom)

---

## Changelog
All notable changes to this project will be documented in this file: [CHANGELOG.md](CHANGELOG.md)

---

## Contributing
We welcome contributions! Please fork the repository and submit a pull request.

---

## Licensing
This project is licensed under the MIT License.

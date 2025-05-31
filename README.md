[![Version](https://img.shields.io/pypi/v/fellow.svg)](https://pypi.org/project/fellow/)
![CI](https://github.com/ManuelZierl/fellow/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/ManuelZierl/fellow/branch/main/graph/badge.svg)](https://codecov.io/gh/ManuelZierl/fellow)


# ![Fellow](img/logo.svg)

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

### Custom Commands
Fellow supports **custom commands**, allowing you to extend its capabilities with your own automation logic — all without modifying the core codebase.

You can define your own commands by placing Python files in `.fellow/commands/`, and then referencing them in your config.

You can also use:
```bash
fellow init-command my_custom_command
```
This will create a new Python file in `.fellow/commands/` with the necessary boilerplate code.

Then, register your command in your config file:
```yaml
...
commands:
    - "my_custom_command"
    - ...
```

With this method, you can also **override existing commands** by using the same name as a built-in one.

---

## Changelog
All notable changes to this project will be documented in this file: [CHANGELOG.md](CHANGELOG.md)

---

## Contributing
We welcome contributions! Please fork the repository and submit a pull request.

---

## Licensing
This project is licensed under the MIT License.
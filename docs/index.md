---
layout: default
title: Welcome
nav_order: 0
---

[![Version](https://img.shields.io/pypi/v/fellow.svg)](https://pypi.org/project/fellow/)
![CI](https://github.com/ManuelZierl/fellow/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/ManuelZierl/fellow/branch/main/graph/badge.svg)](https://codecov.io/gh/ManuelZierl/fellow)

---

## Welcome to <img src="img/logo.svg" alt="drawing" width="100"/>

**Fellow** is a command-line AI assistant built by developers, for developers.

Unlike most AI tools that stop at suggesting code, Fellow goes a step further:  
It *executes* tasks on your behalf. It reasons step-by-step, chooses commands from a plugin system, and edits files, generates content, or writes tests — autonomously.

---

## Table of Contents

1. **[Overview](docs/overview/what-is-fellow.md)**
   - [What is Fellow?](/docs/overview/what-is-fellow/)
   - [Key Concepts](docs/overview/key-concepts.md)
2. **[Usage](docs/usage/installation.md)**
   - [Installation](docs/usage/installation.md)
   - [Running Fellow](docs/usage/running.md)
3. **[Configuration](docs/configuration/index.md)**
4. **[Commands](docs/commands/index.md)**
   - [Built-in Commands](docs/commands/builtin/index.md)
     - [create_file](docs/commands/builtin/create_file.md)
     - [view_file](docs/commands/builtin/view_file.md)
     - [delete_file](docs/commands/builtin/delete_file.md)
     - [edit_file](docs/commands/builtin/edit_file.md)
     - [list_files](docs/commands/builtin/list_files.md)
     - [run_python](docs/commands/builtin/run_python.md)
     - [run_pytest](docs/commands/builtin/run_pytest.md)
     - [list_definitions](docs/commands/builtin/list_definitions.md)
     - [get_code](docs/commands/builtin/get_code.md)
     - [make_plan](docs/commands/builtin/make_plan.md)
     - [summarize_file](docs/commands/builtin/summarize_file.md)
     - [pip_install](docs/commands/builtin/pip_install.md)
   - [Custom Commands](docs/commands/custom/index.md)
     - [Purpose and structure](docs/commands/custom/purpose.md)
     - [How to create?](docs/commands/custom/create.md)
     - [Overriding built-in commands](docs/commands/custom/override.md)
     - [The `run` method and CommandContext](docs/commands/custom/run-method.md)
5. **[Clients](docs/clients/index.md)**
   - [OpenAI Client](docs/clients/openai.md)
   - [Gemini Client](docs/clients/gemini.md)
   - [Custom Clients](docs/clients/custom.md)

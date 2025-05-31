---
layout: default
---

# ![Fellow](img/logo.svg)

[![Version](https://img.shields.io/pypi/v/fellow.svg)](https://pypi.org/project/fellow/)
![CI](https://github.com/ManuelZierl/fellow/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/ManuelZierl/fellow/branch/main/graph/badge.svg)](https://codecov.io/gh/ManuelZierl/fellow)

---

## Welcome to Fellow

**Fellow** is a command-line AI assistant built by developers, for developers.

Unlike most AI tools that stop at suggesting code, Fellow goes a step further:  
It *executes* tasks on your behalf. It reasons step-by-step, chooses commands from a plugin system, and edits files, generates content, or writes tests — autonomously.

layout: default
title: Favicon Test
---

## Installation

```bash
pip install fellow
```

---

## Quick Start

```bash
export OPENAI_API_KEY="your_openai_api_key"
fellow --config task.yml
```

Example config file (`task.yml`):

```yaml
task: |
  write a readme file for this Python project
```

---

## Extend with Custom Commands

```bash
fellow init-command my_custom_command
```

Place it in `.fellow/commands/` and register in your config.

---

This is a test page to see if `custom-head.html` gets injected.

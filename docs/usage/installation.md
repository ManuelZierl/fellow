---
title: Installation
nav_order: 1
parent: Usage
---

# Installation

Fellow is distributed as a Python package via [PyPI](https://pypi.org/project/fellow/).  
You can install it on any system that has Python 3.10 or higher.

---

## Prerequisites

Make sure you have the following installed:

- Python 3.10 or higher  
- pip (Python package manager)

You can check your Python version with:

    python --version

If you have multiple versions of Python installed, you may need to use `python3` and `pip3` instead.

---

## Install via pip

To install Fellow globally:

    pip install fellow

You can now run the `fellow` command from your terminal.

---

## Verify Installation

After installation, verify that Fellow is available:

    fellow --help

You should see a list of available flags and commands.

---

## Set Your API Key

Fellow requires an AI backend to function. Depending on which client you use, you’ll need to set the appropriate API key as an environment variable.

For example:
### OpenAI:
Unix/Linux/macOS:
> export OPENAI_API_KEY=your_key_here

Windows Powershell:
> $env:OPENAI_API_KEY = "your_key_here"


### Gemini:  
Unix/Linux/macOS:
> export GEMINI_API_KEY=your_key_here

Windows Powershell:
> $env:GEMINI_API_KEY = "your_key_here"

If you're using a **custom client**, refer to its documentation to see which environment variables or credentials are required.
Learn more in the [Client documentation](/fellow/clients).

---

Next step: [Running Fellow](/fellow/usage/running)

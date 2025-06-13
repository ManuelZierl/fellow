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

```bash
python --version
```
If you have multiple versions of Python installed, you may need to use `python3` and `pip3` instead.

---

## Install via pip

To install Fellow globally:

```bash
pip install fellow
```

You can now run the `fellow` command from your terminal.

---

## Verify Installation

After installation, verify that Fellow is available:
```bash
fellow --help
```

You should see a list of available flags and commands.

---

## Set Your API Key

Fellow requires an AI backend to function. The recommended way to provide credentials is via:

```bash
fellow add-secret <KEY> <VALUE>
```

For example:

- **OpenAI:**
    ```bash
    fellow add-secret OPENAI_API_KEY your_openai_api_key
    ```

- **Gemini:**
  ```bash
  fellow add-secret GEMINI_API_KEY your_gemini_api_key
  ```

This stores the secret in a local plaintext file (default: `.fellow/.secrets`) and makes it available as an environment variable whenever Fellow runs.

> You can also use standard environment variables (`export KEY=...` or `$env:KEY=...`), but `fellow add-secret` is the recommended approach for convenience and portability.

If needed, you can open the `.fellow/.secrets` file directly to inspect or manually edit your secrets.

The default path can be changed by setting `secrets_path` in your `config.yml`:

```yaml
secrets_path: ".fellow/.secrets"
```

If you're using a **custom client**, check its documentation to see which keys are required.

Learn more in the [Client documentation](/fellow/clients).

---

Next step: [Running Fellow](/fellow/usage/running)

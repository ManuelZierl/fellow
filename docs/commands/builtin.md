---
title: Built-in Commands
nav_order: 1
parent: Commands
---

# Built-in Commands

Fellow includes a variety of built-in commands that can be used out of the box. Each command defines structured inputs and behavior, allowing the AI agent to perform useful operations like editing files, navigating code, or running tests.

Below is a complete reference of all available built-in commands.

## Table of Contents

- [`create_file`](#create_file)
- [`view_file`](#view_file)
- [`delete_file`](#delete_file)
- [`edit_file`](#edit_file)
- [`list_files`](#list_files)
- [`run_python`](#run_python)
- [`run_pytest`](#run_pytest)
- [`list_definitions`](#list_definitions)
- [`get_code`](#get_code)
- [`make_plan`](#make_plan)
- [`pip_install`](#pip_install)
- [`search_files`](#search_files)
- [`summarize_file`](#summarize_file)


---

## `create_file`

Creates an empty file at the given path. If the file already exists, it is left unchanged.

**Input fields:**
- `filepath` *(str)* – The path of the file to create.

---

## `view_file`

Displays the content of a file, optionally between two line numbers.

**Input fields:**
- `filepath` *(str)* – Path to the file  
- `from_line` *(int, optional)* – Start line (1-based)  
- `to_line` *(int, optional)* – End line (inclusive)

---

## `delete_file`

Deletes a file. Directories are not allowed.  

This command is **not included in the default command list** for safety reasons, but you can easily enable it by adding it to your config file:

```yml
commands:
  - delete_file
```

**Input fields:**
- `filepath` *(str)* – Path to the file

---

## `edit_file`

Overwrites the content of a file with the given text.

**Input fields:**
- `filepath` *(str)* – File path to edit  
- `new_text` *(str)* – Replacement content

---

## `list_files`

Recursively lists files and directories starting from a given directory.

**Input fields:**
- `directory` *(str)* – Start directory  
- `max_depth` *(int)* – Max recursion depth (1 = non-recursive)  
- `pattern` *(str, optional)* – Filter by filename substring

---

## `run_python`

Executes a Python script in a subprocess and captures stdout/stderr.

**Input fields:**
- `filepath` *(str)* – Path to `.py` script  
- `args` *(str, optional)* – Command-line arguments

---

## `run_pytest`

Runs pytest on the specified target and returns output.

**Input fields:**
- `target` *(str)* – File or folder to test  
- `args` *(str, optional)* – Extra pytest flags (e.g., `-k test_name`)

---

## `list_definitions`

Extracts function and class signatures from a Python file.

**Input fields:**
- `filepath` *(str)* – Python file to analyze

**Output:**
- Function and class names with argument signatures and docstrings

---

## `get_code`

Extracts the source code of a specific class, function, or method.

**Input fields:**
- `filepath` *(str)* – Python file path  
- `element` *(str)* – Name like `my_func` or `MyClass.my_method`

---

## `make_plan`

Passes a plan string to the currently active AI client via its `set_plan` method.  
It is up to the specific client implementation to decide how the plan is stored, used, or persisted.

For details on how plans are handled, see:

- [OpenAI Client](/fellow/clients/openai)
- [Gemini Client](/fellow/clients/gemini)

**Input fields:**
- `plan` *(str)* – A multi-step plan to guide the assistant's reasoning

---

## `pip_install`

Installs a Python package using pip. Optionally specify a version.

**Input fields:**
- `package_name` *(str)* – Package to install  
- `version` *(str, optional)* – e.g., `1.2.3`

---

## `search_files`

Performs a case-insensitive search for a string in a directory tree.

**Input fields:**
- `directory` *(str)* – Root directory  
- `search` *(str)* – String to look for  
- `extension` *(str, optional)* – Restrict to files with this extension

---

## `summarize_file`

Uses the current AI client to summarize the contents of a text file.

**Input fields:**
- `filepath` *(str)* – File to summarize  
- `max_chars` *(int, optional)* – Limit characters to read

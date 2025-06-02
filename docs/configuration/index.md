---
title: Configuration
nav_order: 3
---

# Configuration

Fellow is configured via a single YAML file passed with the `--config` flag:

    fellow --config task.yml

A minimal config can include just a `task`, but the full set of options gives you fine-grained control over how the assistant behaves, logs, and chooses commands.

---

## Default Configuration

You can view the full default configuration here:

[default_fellow_config.yml on GitHub](https://github.com/ManuelZierl/fellow/blob/main/fellow/default_fellow_config.yml)

This file contains all supported configuration fields with reasonable defaults. You can copy and adapt it for your own use.

---

## Explanation of Fields

### `introduction_prompt`

The system prompt shown to the AI. You can include `{% raw %}{{TASK}}{% endraw %}` to dynamically insert your task text.

### `first_message`

The first message sent to the AI after the system prompt — usually an invitation to begin acting.

### `task`

The main instruction Fellow will execute. Should be plain text or multiline YAML string.

### `log`

Controls whether output is saved to a file and how it is formatted.

- `log.active`: Enable/disable logging
- `log.spoiler`: Whether to wrap logs in collapsible blocks (for Markdown)
- `log.filepath`: Where logs are written (e.g. `fellow_log.md`)

### `ai_client`

Defines which AI backend is used (`openai`, `gemini`, or a custom client) and includes its config.

For detailed per-client config, see:
- [OpenAI Client](/fellow/clients/openai)
- [Gemini Client](/fellow/clients/gemini)
- [Custom Clients](/fellow/clients/custom)

### `commands`

A list of commands the AI can use. These must match the function names registered or implemented.

See [Built-in Commands](/fellow/commands/builtin) for a full list of built-in commands, or [Custom Commands](/fellow/commands/custom) for how to create your own.

### `planning`

Optional planning mode. If active, Fellow will first call [`make_plan`](/fellow/commands/buildin#make_plan) command with the planning prompt.

### `steps_limit`

If set, limits the number of iterations (reasoning + command cycles) in the session. If null, Fellow will run until AI decides to stop.

### `custom_commands_paths`

List of directories to search for custom commands.  

It is recommended to set this to: `.fellow/commands`

This allows you to keep custom command implementations organized and version-controlled in your project root. Commands placed here can be registered in your config and used just like built-in ones.


### `custom_clients_paths`

List of directories to search for custom client implementations.

It is recommended to set this to: `.fellow/clients`

This allows you to define and organize custom AI clients (e.g. for local models or alternative APIs) within your project directory.  
Clients in this folder can be referenced in your config using their module name.

---

If any field is omitted from the config, Fellow will use its internal defaults. You can use this YAML file to define reusable workflows, ensure reproducibility, or override behavior for different environments.

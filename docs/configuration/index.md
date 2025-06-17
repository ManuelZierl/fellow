---
title: Configuration
nav_order: 3
---

# Configuration

Fellow supports two complementary ways of setting configuration:

1. **YAML File (recommended)**  
   Pass a `.yml` config via the `--config` flag:
   
       fellow --config my_task.yml

2. **Command-Line Flags**  
   All options can also be set directly via CLI arguments. This is useful for scripting or temporary overrides.  
   CLI args take precedence over YAML.

Examples:

```bash
fellow --task "Write a README.md for this project" --log.active=true --steps_limit=5
```

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

### `task_id`

A unique identifier (UUID) for this specific run of Fellow.

**Recommendation:** Normally, you should not set this manually. Let Fellow assign it automatically unless you have a specific need.


### `log`

Controls whether output is saved to a file and how it is formatted.

- `log.active`: Enable/disable logging
- `log.spoiler`: Whether to wrap logs in collapsible blocks (for Markdown)
- `log.filepath`: Where logs are written (normally `.fellow/runs/{% raw %}{{task_id}}{% endraw %}/log.md`)


### `memory`

Controls whether the memory state of the run is persisted after completion.

- `memory.log`: Enable/disable writing the memory to disk
- `memory.filepath`: Path to the memory file (must end with `.json`), e.g. `.fellow/runs/{% raw %}{{task_id}}{% endraw %}/memory.json`

### `metadata`

Controls whether metadata about the run (e.g. task details, environment) is stored.

- `metadata.log`: Enable/disable metadata output
- `metadata.filepath`: Path to the metadata file (must end with `.json`), e.g. `.fellow/runs/{% raw %}{{task_id}}{% endraw %}/metadata.json`

### `ai_client`

Defines which AI backend is used (`openai`, `gemini`, or a custom client) and includes its config.

For detailed per-client config, see:
- [OpenAI Client](/fellow/clients/openai)
- [Gemini Client](/fellow/clients/gemini)
- [Custom Clients](/fellow/clients/custom)

### `commands`

Defines which commands the AI is allowed to use, and optionally applies **policies** to them.

```yaml
commands:
  create_file: {}
  view_file: {}
  edit_file:
    policies:
      - name: deny_if_field_in_blacklist
        config:
          fields: [ filepath ]
          blacklist:
            - ".env"
            - "secrets.*"
  run_python: {}
  list_files: {}
  list_definitions: {}
  get_code: {}
  make_plan: {}
  summarize_file: {}
  pip_install: {}
```

Each key is the name of a registered command.  
The value can be an empty dictionary `{}` (to allow the command without restriction), or it can include a `policies:` list to define checks that must pass before the command is executed.

Policies help **enforce safety, access control, or project-specific constraints**.

See also:

- [Built-in Commands](/fellow/commands/builtin)
- [Custom Commands](/fellow/commands/custom)
- [Policy System](/fellow/policies)

### `default_policies`

A list of policies that should be applied to **all commands by default**.

This is useful if you want to enforce global behavior rules (e.g. safety checks, input validation, logging) without having to repeat the same policy configuration for each command individually.

Each entry is a `PolicyConfig` object with the following structure:

```yaml
default_policies:
  - name: YourPolicyName
    config:
      some_key: some_value
```

These policies are applied *in addition to* any command-specific policies. Learn more about how policies work in the [policies documentation](/fellow/policies).


### `planning`

Optional planning mode. If active, Fellow will first call [`make_plan`](/fellow/commands/builtin#make_plan) command with the planning prompt.

### `steps_limit`

If set, limits the number of iterations (reasoning + command cycles) in the session. If null, Fellow will run until AI decides to stop.

### `custom_commands_paths`

List of directories to search for custom commands.  

It is recommended to set this to: `.fellow/commands`

This allows you to keep custom command implementations organized and version-controlled in your project root. Commands placed here can be registered in your config and used just like built-in ones. Learn more about [custom commands](/fellow/commands/custom).

### `custom_clients_paths`

List of directories to search for custom client implementations.

It is recommended to set this to: `.fellow/clients`

This allows you to define and organize custom AI clients (e.g. for local models or alternative APIs) within your project directory.  
Clients in this folder can be referenced in your config using their module name. Learn more about [custom clients](/fellow/clients/custom).

### `custom_policies_paths`

List of directories to search for custom policy implementations.

It is recommended to set this to: `.fellow/policies`

This allows you to define your own policies to control and restrict Fellow’s behavior in specific situations — for example, to limit the number of files a command can modify, or to prevent certain commands from being used on weekends.

Policies in this folder can be registered in your config by name and used like built-in ones. Learn more about [custom policies](/fellow/policies/custom).

### `secrets_path`

Path to the file where Fellow stores and loads secrets (like API keys).

Default: `.fellow/.secrets`

This file is used by the `fellow add-secret` command to persist credentials. At runtime, all entries from this file are automatically loaded as environment variables.

You can change this path if you want to use a centralized or shared secrets file, or if your project requires a different structure.

> 💡 Tip: The `.secrets` file should not be committed to version control. By default, Fellow ensures it is ignored by creating a `.gitignore` file in the `.fellow/` directory.

---

If any field is omitted from the config, Fellow will use its internal defaults. You can use this YAML file to define reusable workflows, ensure reproducibility, or override behavior for different environments.

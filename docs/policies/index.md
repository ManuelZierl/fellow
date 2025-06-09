---
title: Policies
nav_order: 6
has_children: true
---

# Policies

Fellow supports a flexible **policy system** to restrict or guide command execution based on contextual logic.

Policies let you enforce constraints such as:

- File path access rules
- Rate limits
- Required approvals
- Interactive confirmations
- Any custom logic defined by you

This is particularly useful to **prevent hallucinated or dangerous actions** (e.g. deleting important files or running unauthorized Python code).

---

## How It Works

Each command in your config can be associated with one or more policies:

```yaml
commands:
  edit_file:
    policies:
      - name: deny_if_field_in_blacklist
        config:
          fields: [ filepath ]
          blacklist:
            - ".env"
            - "config/secret.yaml"
```

At runtime, Fellow checks all policies before executing a command.

If **any policy fails**, the command is blocked and the reason is logged.

---

## Policy Structure

A policy entry in the config has the form:

```yaml
- name: <policy_name>
  config: <optional_dict_of_config>
```

The `name` refers to a registered policy (either built-in or custom).  
The `config` is an optional dictionary passed to the policy class at runtime.

---

## Policy Evaluation Flow

When the AI chooses to run a command:

1. Fellow collects all associated policies from the config.
2. Each policy is called with:
   - The command name
   - The command handler function
   - The parsed command input
   - The shared context object
3. If **all** policies return success → the command runs.
4. If **any** policy returns failure → execution is aborted and the AI is informed.

---

## Where to Define Policies

- **Built-in** policies are bundled with Fellow. See [Built-in Policies](/fellow/policies/builtin).
- For how to defining **custom** policies see [Custom Policies](/fellow/policies/custom).




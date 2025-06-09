---
title: Built-in Policies
parent: Policies
nav_order: 1
---

# Built-in Policies

Fellow includes some built-in policies to help you restrict sensitive operations. You can reference them by name in your config.

## Table of Contents

- [`deny_if_field_in_blacklist`](#deny_if_field_in_blacklist)
- [`require_user_confirmation`](#require_user_confirmation)


---

## `deny_if_field_in_blacklist`

Blocks a command if certain input fields match blacklisted values.

### Example

```yaml
commands:
  edit_file:
    policies:
      - name: deny_if_field_in_blacklist
        config:
          fields: [ filepath ]
          blacklist:
            - ".env"
            - "secrets.*"
```

### Config Fields

- `fields`: list of input fields to inspect (e.g. `filepath`)
- `blacklist`: list of values or patterns to block

---

## `require_user_confirmation`

Prompts the user for confirmation before allowing the command to run. This is useful for sensitive or potentially destructive actions.

### Example

```yaml
commands:
  delete_file:
    policies:
      - name: require_user_confirmation
        config:
          message: "Are you sure you want to delete this file? Type 'yes' to proceed: "
```

### Config Fields

- `message`: Optional custom message to display. You can include `{command_name}` and `{args}` placeholders.

If the user responds with `y` or `yes`, the command proceeds. Otherwise, it is blocked with a denial message.
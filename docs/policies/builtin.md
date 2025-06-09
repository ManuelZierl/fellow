---
title: Built-in Policies
parent: Policies
nav_order: 1
---

# Built-in Policies

Fellow includes some built-in policies to help you restrict sensitive operations. You can reference them by name in your config.

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

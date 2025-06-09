---
title: Custom Policies
parent: Policies
nav_order: 2
---

# Custom Policies

You can define your own policies to enforce project-specific rules, confirmations, or constraints.

Have an idea that might be useful to others?  
You're warmly invited to [open a pull request](https://github.com/ManuelZierl/fellow) and contribute your policy back to
the community!

Custom policies are placed in `.fellow/policies/` or any directory listed in `custom_policies_paths` in your config.

---

## Quick Start

Create a new policy with:

```bash
fellow init-policy my_policy_name
```

This generates a file like `.fellow/policies/my_policy_name.py` with the basic structure.

---

## Structure

Each custom policy consists of:

- A config class extending `PolicyConfig`
- A policy class extending `Policy[YourConfigClass]`
- A `check(...)` method that returns `True` or an error message

### Example

Below is a minimal working example of a custom policy.

It checks whether a specific string field in the command input (like `filename`) exceeds a maximum allowed length.  
This kind of check can be useful for enforcing naming conventions, preventing long file paths, or limiting user input.

You define a config class to validate the policy's inputs, and a policy class that implements the logic in its
`check(...)` method.

```python
from typing import TYPE_CHECKING, Union
from pydantic import Field
from fellow.policies.Policy import Policy, PolicyConfig

if TYPE_CHECKING:
    from fellow.commands.Command import CommandContext, CommandHandler, CommandInput


class MaxLengthFieldConfig(PolicyConfig):
    field: str = Field(..., description="Name of the CommandInput field to check")
    max_length: int = Field(..., description="Maximum allowed length of the value")


class MaxLengthField(Policy[MaxLengthFieldConfig]):
    def __init__(self, config: MaxLengthFieldConfig):
        self.config = config

    def check(
            self,
            command_name: str,
            command_handler: "CommandHandler",
            args: "CommandInput",
            context: "CommandContext",
    ) -> Union[bool, str]:
        value = getattr(args, self.config.field, None)
        if not isinstance(value, str):
            return True
        if len(value) > self.config.max_length:
            return f"Field '{self.config.field}' exceeds max length {self.config.max_length}: '{value}'"
        return True
```

---

## Usage in Config

After creating your policy, use it in your `commands` config:

```yaml
commands:
  create_file:
    policies:
      - name: max_length_field
        config:
          field: filename
          max_length: 50
```

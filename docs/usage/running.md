---
title: Running Fellow
nav_order: 2
parent: Usage
---

# Running Fellow

Once installed, you can run Fellow using a YAML config file that defines the task and other settings.

At its simplest, you just point Fellow to your configuration file:

    fellow --config task.yml

This will launch the assistant, which will read the task, reason step-by-step, and execute commands as needed.

---

## Minimal Config Example

A minimal `task.yml` might look like this:

```yaml
task: |
  Generate a README file for this project
```

This is often enough to get started, assuming you're using the default settings.

---

## Logging

Fellow logs its thoughts and actions to the console.  
If logging is enabled in the config, it will also write detailed logs to the `.fellow/` directory.

---

## Ending a Session

Fellow automatically ends the loop when:

- The AI outputs a message containing `END`, or  
- The configured step limit is reached
- You manually stop the process (e.g., with `Ctrl+C`)

---

Learn more about available options in the  
[Configuration documentation](fellow/configuration/index.md).

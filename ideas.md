- ideas for commands to add:

pip install

# other ideas

### possible also to define custom commands in a local /commands directory that get joined?

### let it make a plan first and store it as system message?
maybe add command 
    make_plan -> chatgpt creates a plan that is added to the system messages (not deleted or summarized)
    note_down -> chatgpt creates a note that is added to the system messages (summary memory)
make this configurable like:
```yml
planning:
  active: true
  manual_review: true # user can review the plan and edit it if needed
  planning_prompt: "Before you start working on the task you should use the make_plan command to create a plan. This will help you to organize your thoughts and make sure you are on the right track."
  output: "plan.md" # location of the plan file where the plan will be stored so the user can review it, must be set when manual_review is true
 ```


this somehow failed to be parsed:

Thought: I'll now update the ALL_COMMANDS dictionary to include the new pip_install command. I will insert a new entry for "pip_install": (PipInstallInput, pip_install) before the closing curly bracket. Action: { "edit_file": { "filepath": "fellow/commands/init.py", "from_line": 19, "to_line": 20, "new_text": " "summarize_file": (SummarizeFileInput, summarize_file),\n "pip_install": (PipInstallInput, pip_install)\n}" } }

Thought: After updating the command dictionary, I will now edit the fellow/commands/pip_install.py file to add the implementation of the pip_install command as previously described.

### add spoiler to markdown logs
<details>
  <summary>Overview</summary>

Text comes here ...

</details>


### long term memory:
when running fellow multiple times at the same project we can create a memory.json or similar with informations about the project, what it is about e.g that then can be loaded when running the agent again



bug:
{
  "view_file": {
    "filepath": "fellow/commands/__init__.py",
    "from_line": 140,
    "to_line": 160
  }
}
resulted in 
[INFO] No lines to display (start >= end).




### Use funcitoin calling:

memory woul look like htis.

```json
[
  {
    "role": "system",
    "content": "You are an autonomous senior software engineering agent embedded into a structured CLI environment.\n\nYour task: Make yourself familiar with the project, then write a good README file.\n\nAlways explain your reasoning first. If appropriate, call one of the available functions. You can call exactly one function per step."
  },
  {
    "role": "user",
    "content": "Please begin your task."
  },
  {
    "role": "assistant",
    "content": "To understand the project structure, I will begin by listing the files in the root directory up to a depth of 2. This will help identify the key components of the codebase."
  },
  {
    "role": "assistant",
    "function_call": {
      "name": "list_files",
      "arguments": "{ \"directory\": \".\", \"max_depth\": 2 }"
    }
  },
  {
    "role": "function",
    "name": "list_files",
    "content": ".git/\n  HEAD\n  config\nREADME.md\nsetup.py\nfellow/\n  main.py\n  clients/\n  commands/\nrequirements.txt\n"
  },
  {
    "role": "assistant",
    "content": "I can see the project includes a `fellow/` source directory, a `README.md` file, and a `setup.py` which likely contains metadata about the project. I will check the contents of `README.md` next to see what documentation already exists."
  },
  {
    "role": "assistant",
    "function_call": {
      "name": "view_file",
      "arguments": "{ \"filepath\": \"README.md\" }"
    }
  },
  {
    "role": "function",
    "name": "view_file",
    "content": "[INFO] The file is empty or the specified range contains no lines."
  },
  {
    "role": "assistant",
    "content": "The `README.md` file is empty, so I will create the documentation from scratch. I'll now inspect `setup.py` to extract metadata like the project description and dependencies."
  },
  {
    "role": "assistant",
    "function_call": {
      "name": "view_file",
      "arguments": "{ \"filepath\": \"setup.py\" }"
    }
  },
  {
    "role": "function",
    "name": "view_file",
    "content": "from setuptools import setup\n\nsetup(\n    name=\"fellow\",\n    version=\"0.0.1\",\n    description=\"Fellow CLI tool is a command line development assistant\",\n    ...\n)"
  },
  {
    "role": "assistant",
    "content": "The `setup.py` file describes the project as a 'command line development assistant'. The main entry point is `fellow.main:main`, and dependencies are managed via `install_requires`. Now, I’ll draft a new README file with an introduction, features, and installation steps."
  },
  {
    "role": "assistant",
    "function_call": {
      "name": "edit_file",
      "arguments": "{ \"filepath\": \"README.md\", \"new_text\": \"# Fellow CLI Tool\\n\\nFellow is a command-line development assistant...\" }"
    }
  },
  {
    "role": "function",
    "name": "edit_file",
    "content": "[OK] Edited file: README.md"
  },
  {
    "role": "assistant",
    "content": "The README file has been written successfully. I’ve included the project description, features, installation, usage, and license. Task complete."
  },
  {
    "role": "assistant",
    "content": "END"
  }
]

```
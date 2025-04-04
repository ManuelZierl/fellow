# Fellow CLI Tool

Fellow is a command-line development assistant empowering developers to interact with AI for executing tasks efficiently. It is built to leverage OpenAI's capabilities to interpret tasks, execute commands, and automate workflows.

## Features
- Seamlessly integrates AI to facilitate development tasks.
- Customize commands through YAML configuration.
- Supports logging of interactions and task executions.
- Uses OpenAI for intelligent command processing.

## Installation

To install Fellow, clone this repository and set up the required environment:

```bash
$ git clone <repository-url>
$ cd fellow
$ pip install -r requirements.txt
```

## Usage

Run the Fellow CLI with the following command:

```bash
$ fellow --config <path-to-config.yml> --task "Your task description"
```

Additional arguments include:
- `--commands`: Specify which commands to load from configuration.
- `--log`: Define a logging file location.

## Configuration

Customize your fellow experience via the `fellow_config.yml`. Refer to `default_fellow_config.yml` for available configuration options.

## Contributing

Contributions are welcome! Please fork the repository, make necessary changes, and create a pull request.

## License

This project is licensed under the terms of the MIT License. See the LICENSE file for details.

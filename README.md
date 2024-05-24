# Bills Analyzer

A collection of scripts to extract structured data from utility bills.

```sh
poetry run process_utility_bill gas path/to/file.pdf [password]
poetry run process_utility_bill --help
```

## Development


### Setup

1. Install [Poetry](https://python-poetry.org/docs/).
2. ```sh
   cd $PROJECT_ROOT  # project root
   poetry install --with=dev
   ```

### Commands

* Activate an environment with the development python and tools: `poetry shell`
* Run a tool from outside of the environment or a poetry script: `poetry run ...`
  * `poetry run nox` to execute build steps, like linting, using [Nox](https://nox.thea.codes/en/stable/index.html). Use `-r` to minimize setup time by reusing the venv for each session.
* For all commands: `poetry list`

### Suggested IDE Plugins
Sublime Text
* SublimeLinter with linters
* LSP
* Python Black
* isorted
* Markdown Preview

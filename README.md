# Bills Analyzer

A collection of scripts to extract structured data from utility bills.

```sh
poetry run process_utility_bill gas path/to/file.pdf [password]
poetry run process_utility_bill --help
```

## Development


### Setup

Setup local repo with global tools, venv, and git hooks
```sh
cd $PROJECT_ROOT  # project root
./scripts/setup_repo.sh
```

Using the virtual env in-project can be globally set with `poetry config virtualenvs.in-project true`

### Commands

TODO: does the venv need to be activated if poetry commands are used?

* Activate an environment with the development python and tools: `poetry shell`
* Run a tool from outside of the environment or a poetry script: `poetry run ...`
  * `poetry run pytests` to execute tests,
* Run build pipeline using `nox` Use `-r` to minimize setup time by reusing the nox virtual environments for each session.
* For all commands: `poetry list` and `nox --list-sessions`

### Suggested IDE Plugins
Sublime Text
* SublimeLinter with linters
* LSP
* Python Black
* isort
* Markdown Preview

### Code and documentation styles

For the most part, the styles are enforced with tools integrated into `pre-commit`.

docstring: [google](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

> Here are three useful guidelines about documenting test cases:
>
> 1. State the expected behaviour and be specific about it.
> 2. Omit everything that already follows from the fact that it is a test case. For example, avoid words like “test if”, “correctly”, “should”.
> 3. Use “it” to refer to the system under test. There is no need to repeatedly name the function or class you are testing. (A better place for that is the docstring of the test module, or the test class if you use those.)
>
> https://cjolowicz.github.io/posts/hypermodern-python-05-documentation/#adding-docstrings-to-the-test-suite

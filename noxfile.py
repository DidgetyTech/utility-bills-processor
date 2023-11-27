# noqa: D100
import nox


@nox.session(python=["3.10"])
def lint(session):
    """Perform static analysis."""
    session.install("poetry")
    session.run("poetry", "install", "--with=dev")
    session.run("isort", ".")
    session.run("black", ".")
    session.run("flake8")
    session.run("mypy", "--config-file", "pyproject.toml")

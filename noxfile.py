# noqa: D100
import nox


@nox.session(python=["3.12"])
def lint(session):
    """Perform static analysis."""
    session.install("poetry")
    session.run("poetry", "install", "--with=dev")
    session.run("isort", ".")
    session.run("black", ".")
    session.run("flake8")
    session.run("mypy", "--config-file", "pyproject.toml")


@nox.session(python=["3.12"])
def test_locally(session):
    """Run tests that don't need networked resources."""
    session.install("poetry")
    session.run("poetry", "install", "--with=dev")
    session.run("python", "-m", "unittest")

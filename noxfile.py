# noqa: D100
import nox


@nox.session(python=["3.12"])
def lint(session):
    """Perform static analysis."""
    session.install("pre-commit")
    session.install("poetry")
    session.run("poetry", "install", "--with=dev")
    session.run("pre-commit", "install")
    session.run("pre-commit", "run", "--all")
    session.run("mypy", "--config-file", "pyproject.toml")


@nox.session(python=["3.12"])
def test_locally(session):
    """Run tests that don't need networked resources."""
    session.install("poetry")
    session.run("poetry", "install", "--with=dev")
    session.run("python", "-m", "unittest")

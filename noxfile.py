# noqa: D100
from nox_poetry import session


@session(python=["3.12"])
def test_locally(session):
    """Run tests that don't need networked resources."""
    session.install("pytest", ".")
    session.run("python", "-m", "pytest")

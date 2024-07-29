from nox_poetry import session


@session(python=["3.12"])
def test_locally(session):
    """Run tests that don't need networked resources."""
    args = session.posargs or ["--cov"]
    session.run_always("poetry", "install", "--with", "dev", external=True)
    session.run("python", "-m", "pytest", *args)

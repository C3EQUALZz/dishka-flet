from dataclasses import dataclass

import nox


nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True
nox.options.stop_on_first_error = True


DISHKA_VERSIONS = ["1.7.0", None]
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]


@dataclass(frozen=True, slots=True)
class IntegrationEnv:
    library: str
    version: str

    def get_version(self) -> str:
        """Return version string for installation."""
        return self.version


FLET_ENVS = [
    *[(IntegrationEnv("flet", "0.28.3"), py_version) for py_version in PYTHON_VERSIONS],
    *[(IntegrationEnv("flet", "latest"), py_version) for py_version in PYTHON_VERSIONS],
]


def install_command(dependency: str, version: str | None = None) -> str:
    """Return install command for a specific dependency."""
    return f"{dependency}=={version}" if version else dependency


def load_test_dependencies() -> list[str]:
    """Load development dependencies from pyproject.toml."""
    toml_data = nox.project.load_toml("pyproject.toml")
    return toml_data["dependency-groups"]["test"]


@nox.session()
@nox.parametrize("flet_env,python", FLET_ENVS)
@nox.parametrize("dishka_version", DISHKA_VERSIONS)
def tests(
    session: nox.Session,
    flet_env: IntegrationEnv,
    dishka_version: str | None,
) -> None:
    """Run tests with different versions of dependencies."""
    session.install(install_command("dishka", dishka_version))

    # Install flet version
    if flet_env.version == "latest":
        session.install("flet[all]")
    else:
        session.install(f"flet[all]=={flet_env.version}")

    dev_deps = load_test_dependencies()
    session.install(*dev_deps)

    session.install("-e", ".")

    session.run(
        "pytest",
        "tests",
        "--cov=dishka_flet",
        "--cov-report=term-missing",
        "--cov-append",
        "--cov-config=.coveragerc",
        env={
            "COVERAGE_FILE": f".coverage.{session.name}",
        },
        *session.posargs,
    )


@nox.session
def coverage(session: nox.Session) -> None:
    """Generate and view coverage report."""
    session.install("coverage")
    session.run("coverage", "combine")
    session.run("coverage", "report", "--fail-under=80")

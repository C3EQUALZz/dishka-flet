from importlib.metadata import version as get_package_version
from typing import Final, ParamSpec, TypeVar

import flet
from packaging import version


def get_current_flet_library_version() -> version.Version:
    flet_version = getattr(flet, "__version__", None)
    if flet_version:
        return version.parse(flet_version)
    return version.parse(get_package_version("flet"))


ReturnT = TypeVar("ReturnT")
ParamsP = ParamSpec("ParamsP")

CONTAINER_NAME: Final[str] = "dishka_container"
FLET_CURRENT_VERSION: Final[version.Version] = get_current_flet_library_version()
FLET_028_VERSION: Final[version.Version] = version.parse("0.28.3")
FLET_080_VERSION: Final[version.Version] = version.parse("0.80.0")

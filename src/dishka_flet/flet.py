__all__ = ("inject", "setup_dishka")

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, Final, overload

import flet
from dishka import AsyncContainer, Container

from dishka_flet._consts import (
    FLET_028_VERSION,
    FLET_080_VERSION,
    FLET_CURRENT_VERSION,
    ParamsP,
    ReturnT,
)
from dishka_flet._injectors import inject_async, inject_sync

CONTAINER_NAME: Final[str] = "dishka_container"


@overload
def inject(func: Callable[ParamsP, ReturnT]) -> Callable[..., ReturnT]: ...


@overload
def inject(
    func: Callable[ParamsP, Awaitable[ReturnT]],
) -> Callable[..., Awaitable[ReturnT]]: ...


def inject(
    func: Callable[ParamsP, Any],
) -> Any:
    """Inject dependencies into a function using dishka.

    This decorator removes parameters annotated with FromDishka from the
    function signature, injecting them automatically at runtime.

    Note: The return type uses overload to preserve type information.
    At runtime, parameters with FromDishka annotations are removed.
    """
    # BaseControl is only available in flet 0.80.0 and above
    if FLET_CURRENT_VERSION >= FLET_080_VERSION and "BaseControl" not in func.__globals__:
        func.__globals__["BaseControl"] = flet.BaseControl

    if inspect.iscoroutinefunction(func):
        return inject_async(func)

    return inject_sync(func)


def setup_dishka(
    container: AsyncContainer | Container,
    page: flet.Page,
) -> None:
    if FLET_CURRENT_VERSION <= FLET_028_VERSION:
        page.session.set(CONTAINER_NAME, container)  # type: ignore[attr-defined]
    else:
        page.session.store.set(CONTAINER_NAME, container)

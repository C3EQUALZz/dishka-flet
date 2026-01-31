__all__ = ("FletProvider", "inject", "setup_dishka")

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, overload

import flet
from dishka import AsyncContainer, Container, Provider, Scope, from_context

from dishka_flet._consts import (
    CONTAINER_NAME,
    FLET_028_VERSION,
    FLET_080_VERSION,
    FLET_CURRENT_VERSION,
    ParamsP,
    ReturnT,
)
from dishka_flet._injectors import inject_async, inject_sync


class FletProvider(Provider):
    page = from_context(flet.Page, scope=Scope.REQUEST)


@overload
def inject(func: Callable[ParamsP, ReturnT]) -> Callable[..., ReturnT]: ...


@overload
def inject(
    func: Callable[ParamsP, Awaitable[ReturnT]],
) -> Callable[..., Awaitable[ReturnT]]: ...


def inject(
    func: Callable[ParamsP, Any],
) -> Any:
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

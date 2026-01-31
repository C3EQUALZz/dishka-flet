__all__ = ("inject", "setup_dishka")

from collections.abc import Callable
from typing import Final

import flet
from dishka import AsyncContainer, Container
from dishka.integrations.base import wrap_injection

from dishka_flet._consts import (
    FLET_028_VERSION,
    FLET_080_VERSION,
    FLET_CURRENT_VERSION,
    ParamsP,
    ReturnT,
)
from dishka_flet._getters import get_container_from_args_kwargs

CONTAINER_NAME: Final[str] = "dishka_container"


def inject(func: Callable[ParamsP, ReturnT]) -> Callable[..., ReturnT]:
    # BaseControl is only available in flet 0.80.0 and above
    if FLET_CURRENT_VERSION >= FLET_080_VERSION and "BaseControl" not in func.__globals__:
        func.__globals__["BaseControl"] = flet.BaseControl

    return wrap_injection(
        func=func,
        container_getter=get_container_from_args_kwargs,
        remove_depends=True,
        is_async=True,
        manage_scope=True,
    )


def setup_dishka(
    container: AsyncContainer | Container,
    page: flet.Page,
) -> None:
    if FLET_CURRENT_VERSION <= FLET_028_VERSION:
        page.session.set(CONTAINER_NAME, container)  # type: ignore[attr-defined]
    else:
        page.session.store.set(CONTAINER_NAME, container)

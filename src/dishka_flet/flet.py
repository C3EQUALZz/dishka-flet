__all__ = ("inject", "setup_dishka")

from collections.abc import Callable
from typing import Any, Final, ParamSpec, TypeVar, cast

import flet
from dishka import AsyncContainer, Container
from dishka.integrations.base import wrap_injection
from flet import BaseControl, ControlEvent, Page
from packaging import version

_ReturnT = TypeVar("_ReturnT")
_ParamsP = ParamSpec("_ParamsP")

CONTAINER_NAME: Final[str] = "dishka_container"

FLET_CURRENT_VERSION: Final[version.Version] = version.parse(flet.__version__)
FLET_028_VERSION: Final[version.Version] = version.parse("0.28.3")


def inject(func: Callable[_ParamsP, _ReturnT]) -> Callable[..., _ReturnT]:
    if FLET_CURRENT_VERSION >= FLET_028_VERSION and "BaseControl" not in func.__globals__:
        func.__globals__["BaseControl"] = BaseControl

    return wrap_injection(
        func=func,
        container_getter=_get_container_from_args_kwargs,
        remove_depends=True,
        is_async=True,
        manage_scope=True,
    )


def _get_container_from_args_kwargs(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> AsyncContainer:
    event: ControlEvent | None = kwargs.get("event")

    if event is None and args:
        first_arg = args[0]
        if hasattr(first_arg, "page"):
            event = first_arg

    if event is None:
        for value in kwargs.values():
            if hasattr(value, "page"):
                event = value
                break

    if event is None:
        msg = (
            "Cannot find event with page attribute. "
            "Make sure your function receives an event parameter (e.g., ControlEvent)."
        )
        raise ValueError(msg)

    page: Page = cast("Page", event.page)
    container: AsyncContainer | None

    if flet.__version__ <= "0.28.3":
        container = page.session.get(CONTAINER_NAME)  # type: ignore[attr-defined]
    else:
        container = page.session.store.get(CONTAINER_NAME)

    if container is None:
        msg = (
            f"Container not found in page.session['{CONTAINER_NAME}']. "
            "Make sure you called setup_dishka() before using inject()."
        )
        raise ValueError(msg)

    return container


def setup_dishka(
    container: AsyncContainer | Container,
    page: Page,
) -> None:
    if FLET_CURRENT_VERSION <= FLET_028_VERSION:
        page.session.set(CONTAINER_NAME, container)  # type: ignore[attr-defined]
    else:
        page.session.store.set(CONTAINER_NAME, container)

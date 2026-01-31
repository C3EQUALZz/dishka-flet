from typing import Any, cast

import flet
from dishka import AsyncContainer, Container
from dishka.exception_base import DishkaError

from dishka_flet._consts import CONTAINER_NAME, FLET_028_VERSION, FLET_CURRENT_VERSION


def get_page_from_args_kwargs(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> flet.Page:
    event: flet.ControlEvent | None = kwargs.get("event")

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
        raise DishkaError(msg)

    return cast("flet.Page", event.page)


def get_container_from_page(
    page: flet.Page,
) -> AsyncContainer | Container:
    container: AsyncContainer | Container | None

    if FLET_CURRENT_VERSION <= FLET_028_VERSION:
        container = page.session.get(CONTAINER_NAME)  # type: ignore[attr-defined]
    else:
        container = page.session.store.get(CONTAINER_NAME)

    if container is None:
        msg = (
            f"Container not found in page.session['{CONTAINER_NAME}']. "
            "Make sure you called setup_dishka() before using inject()."
        )
        raise DishkaError(msg)

    return container


def get_async_container_from_args_kwargs(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> AsyncContainer:
    page: flet.Page = get_page_from_args_kwargs(args, kwargs)

    container: AsyncContainer | Container = get_container_from_page(page)

    if not isinstance(container, AsyncContainer):
        msg = "Expected AsyncContainer"
        raise DishkaError(msg)

    return container


def get_sync_container_from_args_kwargs(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Container:
    page: flet.Page = get_page_from_args_kwargs(args, kwargs)

    container: AsyncContainer | Container = get_container_from_page(page=page)

    if not isinstance(container, Container):
        msg = "Expected Container"
        raise DishkaError(msg)

    return container


def get_context_from_args_kwargs(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[Any, Any]:
    page: flet.Page = get_page_from_args_kwargs(args, kwargs)

    return {
        flet.Page: page,
    }

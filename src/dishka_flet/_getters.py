from typing import TYPE_CHECKING, Any, cast

from dishka import AsyncContainer

from dishka_flet._consts import CONTAINER_NAME, FLET_028_VERSION, FLET_CURRENT_VERSION

if TYPE_CHECKING:
    import flet


def get_container_from_args_kwargs(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> AsyncContainer:
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
        raise ValueError(msg)

    page: flet.Page = cast("flet.Page", event.page)
    container: AsyncContainer | None

    if FLET_CURRENT_VERSION <= FLET_028_VERSION:
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

from collections.abc import Awaitable, Callable

from dishka.integrations.base import wrap_injection

from dishka_flet._consts import ParamsP, ReturnT
from dishka_flet._getters import (
    get_async_container_from_args_kwargs,
    get_context_from_args_kwargs,
    get_sync_container_from_args_kwargs,
)


def inject_async(
    func: Callable[ParamsP, Awaitable[ReturnT]],
) -> Callable[..., Awaitable[ReturnT]]:
    return wrap_injection(
        func=func,
        container_getter=get_async_container_from_args_kwargs,
        remove_depends=True,
        is_async=True,
        manage_scope=True,
        provide_context=get_context_from_args_kwargs,
    )


def inject_sync(func: Callable[ParamsP, ReturnT]) -> Callable[..., ReturnT]:
    return wrap_injection(
        func=func,
        container_getter=get_sync_container_from_args_kwargs,
        remove_depends=True,
        is_async=False,
        manage_scope=True,
        provide_context=get_context_from_args_kwargs,
    )

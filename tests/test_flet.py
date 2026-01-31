from typing import Any
from unittest.mock import Mock

import pytest
from dishka import make_async_container, make_container
from dishka.exception_base import DishkaError
from flet import ControlEvent

from dishka_flet import (
    FromDishka,
    inject,
    setup_dishka,
)

from .common import (
    APP_DEP_VALUE,
    FLET_028_VERSION,
    REQUEST_DEP_VALUE,
    AppDep,
    AppProvider,
    MockControlEvent,
    MockPage,
    RequestDep,
    dishka_page,
    get_current_flet_library_version,
)


async def handler_with_app(
    event: ControlEvent,  # noqa: ARG001
    a: FromDishka[AppDep],
    mock: FromDishka[Mock],
) -> str:
    mock(a)
    return "passed"


@pytest.mark.asyncio()
async def test_app_dependency(app_provider: AppProvider) -> None:
    async with dishka_page(app_provider) as (_page, event):
        handler = inject(handler_with_app)
        result = await handler(event)

        assert result == "passed"
        app_provider.mock.assert_called_with(APP_DEP_VALUE)
        app_provider.app_released.assert_not_called()
    app_provider.app_released.assert_called()


async def handler_with_request(
    event: ControlEvent,  # noqa: ARG001
    a: FromDishka[RequestDep],
    mock: FromDishka[Mock],
) -> str:
    mock(a)
    return "passed"


@pytest.mark.asyncio()
async def test_request_dependency(app_provider: AppProvider) -> None:
    async with dishka_page(app_provider) as (_page, event):
        handler = inject(handler_with_request)
        result = await handler(event)

        assert result == "passed"
        app_provider.mock.assert_called_with(REQUEST_DEP_VALUE)
        app_provider.request_released.assert_called_once()


async def handler_with_event_as_kwarg(
    event: ControlEvent,  # noqa: ARG001
    a: FromDishka[AppDep],
    mock: FromDishka[Mock],
) -> str:
    mock(a)
    return "passed"


@pytest.mark.asyncio()
async def test_event_as_kwarg(app_provider: AppProvider) -> None:
    async with dishka_page(app_provider) as (_page, event):
        handler = inject(handler_with_event_as_kwarg)
        result = await handler(event=event)

        assert result == "passed"
        app_provider.mock.assert_called_with(APP_DEP_VALUE)


async def handler_with_event_as_first_arg(
    event: ControlEvent,  # noqa: ARG001
    a: FromDishka[AppDep],
    mock: FromDishka[Mock],
) -> str:
    mock(a)
    return "passed"


@pytest.mark.asyncio()
async def test_event_as_first_arg(app_provider: AppProvider) -> None:
    async with dishka_page(app_provider) as (_page, event):
        handler = inject(handler_with_event_as_first_arg)
        result = await handler(event)

        assert result == "passed"
        app_provider.mock.assert_called_with(APP_DEP_VALUE)


async def handler_with_event_in_kwargs(
    _some_param: str,
    a: FromDishka[AppDep],
    mock: FromDishka[Mock],
    **kwargs: Any,  # noqa: ARG001
) -> str:
    mock(a)
    return "passed"


@pytest.mark.asyncio()
async def test_event_in_kwargs_values(app_provider: AppProvider) -> None:
    async with dishka_page(app_provider) as (_page, event):
        handler = inject(handler_with_event_in_kwargs)
        result = await handler("test", some_other_param=event)  # type: ignore[no-untyped-call]

        assert result == "passed"
        app_provider.mock.assert_called_with(APP_DEP_VALUE)


@pytest.mark.asyncio()
async def test_missing_event_raises_error(app_provider: AppProvider) -> None:
    async with dishka_page(app_provider) as (_page, _event):
        handler = inject(handler_with_app)

        with pytest.raises(DishkaError, match="Cannot find event with page attribute"):
            await handler("not_an_event")


@pytest.mark.asyncio()
async def test_missing_container_raises_error() -> None:
    page = MockPage()
    event = MockControlEvent(page)

    async def handler_without_setup(
        _event: ControlEvent,
        _a: FromDishka[AppDep],
    ) -> str:
        return "passed"

    handler = inject(handler_without_setup)

    with pytest.raises(DishkaError, match="Container not found"):
        await handler(event)


@pytest.mark.asyncio()
async def test_setup_dishka_stores_container(
    app_provider: AppProvider,
) -> None:
    page = MockPage()
    container = make_async_container(app_provider)

    setup_dishka(container, page=page)  # type: ignore[arg-type,unused-ignore]

    if get_current_flet_library_version() == FLET_028_VERSION:
        stored_container = page.session.get("dishka_container")
    else:
        stored_container = page.session.store.get("dishka_container")

    assert stored_container is container
    await container.close()


@pytest.mark.asyncio()
async def test_async_handler_with_sync_container_raises(
    app_provider: AppProvider,
) -> None:
    """Test that async handler raises error when sync container is used."""
    page = MockPage()
    sync_container = make_container(app_provider)
    setup_dishka(sync_container, page=page)  # type: ignore[arg-type]

    @inject
    async def async_handler(
        event: ControlEvent,  # noqa: ARG001
        _a: FromDishka[AppDep],
    ) -> str:
        return "passed"

    event = MockControlEvent(page)

    with pytest.raises(DishkaError, match="Expected AsyncContainer"):
        await async_handler(event)


@pytest.mark.asyncio()
async def test_sync_handler_with_async_container_raises(
    app_provider: AppProvider,
) -> None:
    """Test that sync handler raises error when async container is used."""
    page = MockPage()
    async_container = make_async_container(app_provider)
    setup_dishka(async_container, page=page)  # type: ignore[arg-type]

    @inject
    def sync_handler(
        event: ControlEvent,  # noqa: ARG001
        _a: FromDishka[AppDep],
    ) -> str:
        return "passed"

    event = MockControlEvent(page)

    with pytest.raises(DishkaError, match="Expected Container"):
        sync_handler(event)

    await async_container.close()

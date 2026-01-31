from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from importlib.metadata import version as get_package_version
from typing import Any, NewType
from unittest.mock import Mock

import flet
from dishka import (
    Provider,
    Scope,
    from_context,
    make_async_container,
    provide,
)
from dishka.entities.depends_marker import FromDishka
from packaging import version

from dishka_flet import setup_dishka

ContextDep = NewType("ContextDep", str)
StepDep = NewType("StepDep", str)

AppDep = NewType("AppDep", str)
APP_DEP_VALUE = AppDep("APP")

RequestDep = NewType("RequestDep", str)
REQUEST_DEP_VALUE = RequestDep("REQUEST")

AppMock = NewType("AppMock", Mock)


def get_current_flet_library_version() -> version.Version:
    """Get current flet version."""
    flet_version = getattr(flet, "__version__", None)
    if flet_version:
        return version.parse(flet_version)
    return version.parse(get_package_version("flet"))


FLET_CURRENT_VERSION = get_current_flet_library_version()
FLET_028_VERSION = version.parse("0.28.3")
FLET_080_VERSION = version.parse("0.80.0")


class AppProvider(Provider):
    context = from_context(provides=ContextDep, scope=Scope.REQUEST)

    def __init__(self) -> None:
        super().__init__()
        self.app_released = Mock()
        self.request_released = Mock()
        self.mock = Mock()
        self._app_mock = AppMock(Mock())

    @provide(scope=Scope.APP)
    def app(self) -> Iterable[AppDep]:
        yield APP_DEP_VALUE
        self.app_released()

    @provide(scope=Scope.REQUEST)
    def request(self) -> Iterable[RequestDep]:
        yield REQUEST_DEP_VALUE
        self.request_released()

    @provide(scope=Scope.REQUEST)
    def get_mock(self) -> Mock:
        return self.mock

    @provide(scope=Scope.APP)
    def app_mock(self) -> AppMock:
        return self._app_mock

    @provide(scope=Scope.STEP)
    def step(self, request: FromDishka[RequestDep]) -> StepDep:
        return StepDep(f"step for {request}")


class MockStore:
    """Mock store for flet 0.80+ session.store."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value


class MockSession:
    """Mock session that adapts to different flet versions."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        if FLET_CURRENT_VERSION >= FLET_080_VERSION:
            self.store = MockStore()

    def get(self, key: str) -> Any:
        """Get value from session (for flet <= 0.28.3)."""
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in session (for flet <= 0.28.3)."""
        self._data[key] = value


class MockPage:
    """Mock Flet page."""

    def __init__(self) -> None:
        self.session = MockSession()


@dataclass
class MockControlEvent:
    """Mock Flet control event."""

    page: MockPage


@asynccontextmanager
async def dishka_page(
    provider: AppProvider,
) -> AsyncIterator[tuple[MockPage, MockControlEvent]]:
    """Context manager for setting up dishka with a mock page."""
    page = MockPage()
    event = MockControlEvent(page)

    container = make_async_container(provider)
    setup_dishka(container, page=page)  # type: ignore[arg-type]

    yield page, event

    await container.close()

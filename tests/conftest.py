"""Shared fixtures for falx tests.

Exposes programmable fakes for the three external boundaries used by falx:
``FalClient``, ``Uploader``, ``Downloader``.

Tests import ``FakeFalClient`` / ``FakeUploader`` / ``FakeDownloader`` directly
from ``tests.conftest`` (pytest auto-discovery makes them importable via the
fixtures ``fal_client`` / ``uploader`` / ``downloader``).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@dataclass(frozen=True)
class SubmitHandle:
    request_id: str
    response_url: str
    status_url: str
    cancel_url: str


@dataclass(frozen=True)
class JobStatus:
    state: str
    queue_position: int | None = None
    logs: list[dict[str, Any]] | None = None
    metrics: dict[str, Any] | None = None
    error: str | None = None
    error_type: str | None = None


class FalAPIError(Exception):
    """Mirrors ``fal_client.FalClientHTTPError`` for boundary tests."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str | None = None,
    ) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.error_type = error_type


@dataclass
class FakeFalClient:
    """Programmable, in-memory stand-in for the real fal_client adapter.

    Default behaviour (no programming calls):
      - ``submit`` returns a synthesised SubmitHandle whose request_id is
        ``req-0001``, ``req-0002``, ...
      - ``status`` returns ``IN_QUEUE`` with ``queue_position=0``
      - ``result`` raises ``KeyError``
      - ``cancel`` is a no-op

    Programming calls override the default behaviour for the remainder of the
    test. Pass either a plain value to return, an exception instance to raise,
    or a callable taking the same arguments as the method.
    """

    submit_calls: list[tuple[str, dict[str, Any], dict[str, str] | None]] = field(
        default_factory=list
    )
    submitted_request_ids: list[str] = field(default_factory=list)
    status_calls: list[tuple[str, str]] = field(default_factory=list)
    result_calls: list[tuple[str, str]] = field(default_factory=list)
    cancel_calls: list[tuple[str, str]] = field(default_factory=list)

    _submit: Any = None
    _status: dict[str, Any] = field(default_factory=dict)
    _result: dict[str, Any] = field(default_factory=dict)
    _cancel: Any = None

    def program_submit(
        self,
        response: SubmitHandle
        | Exception
        | Callable[[str, dict[str, Any], dict[str, str] | None], SubmitHandle],
    ) -> None:
        self._submit = response

    def program_status(self, request_id: str, value: JobStatus | Exception) -> None:
        self._status[request_id] = value

    def program_result(self, request_id: str, value: dict[str, Any] | Exception) -> None:
        self._result[request_id] = value

    def program_cancel(
        self, response: None | Exception | Callable[[str, str], None] = None
    ) -> None:
        self._cancel = response

    async def submit(
        self,
        app_id: str,
        arguments: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
    ) -> SubmitHandle:
        self.submit_calls.append((app_id, dict(arguments), dict(headers) if headers else None))
        if self._submit is None:
            rid = f"req-{len(self.submit_calls):04d}"
            base = f"https://queue.fal.run/{app_id}/requests/{rid}"
            handle = SubmitHandle(
                request_id=rid,
                response_url=base,
                status_url=base + "/status",
                cancel_url=base + "/cancel",
            )
            self.submitted_request_ids.append(handle.request_id)
            return handle
        if isinstance(self._submit, BaseException):
            raise self._submit
        if callable(self._submit):
            handle = cast(SubmitHandle, self._submit(app_id, arguments, headers))
            self.submitted_request_ids.append(handle.request_id)
            return handle
        handle = cast(SubmitHandle, self._submit)
        self.submitted_request_ids.append(handle.request_id)
        return handle

    async def status(self, app_id: str, request_id: str) -> JobStatus:
        self.status_calls.append((app_id, request_id))
        value = self._status.get(request_id)
        if value is None:
            return JobStatus(state="IN_QUEUE", queue_position=0)
        if isinstance(value, BaseException):
            raise value
        return cast(JobStatus, value)

    async def result(self, app_id: str, request_id: str) -> dict[str, Any]:
        self.result_calls.append((app_id, request_id))
        if request_id not in self._result:
            raise KeyError(f"No programmed result for request_id={request_id!r}")
        value = self._result[request_id]
        if isinstance(value, BaseException):
            raise value
        return cast(dict[str, Any], value)

    async def cancel(self, app_id: str, request_id: str) -> None:
        self.cancel_calls.append((app_id, request_id))
        if self._cancel is None:
            return
        if isinstance(self._cancel, BaseException):
            raise self._cancel
        if callable(self._cancel):
            self._cancel(app_id, request_id)


@dataclass
class FakeUploader:
    """Records uploads; returns a deterministic CDN-like URL per path."""

    uploads: list[Path] = field(default_factory=list)

    def upload(self, path: Path) -> str:
        self.uploads.append(Path(path))
        return f"https://cdn.fal.local/{Path(path).name}"


@dataclass
class FakeDownloader:
    """Records downloads and writes a dummy payload to ``dest``."""

    downloads: list[tuple[str, Path]] = field(default_factory=list)

    def download(self, url: str, dest: Path) -> None:
        self.downloads.append((url, Path(dest)))
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Path(dest).write_bytes(f"fake-content-for:{url}".encode())


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def fal_client() -> FakeFalClient:
    return FakeFalClient()


@pytest.fixture
def uploader() -> FakeUploader:
    return FakeUploader()


@pytest.fixture
def downloader() -> FakeDownloader:
    return FakeDownloader()


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def copy_fixture(tmp_path: Path) -> Callable[[str], Path]:
    """Copy a file from tests/fixtures/ into tmp_path and return the new path."""

    def _copy(name: str) -> Path:
        src = FIXTURES_DIR / name
        dst = tmp_path / name
        dst.write_bytes(src.read_bytes())
        return dst

    return _copy

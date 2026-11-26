"""Core primitives for fal.ai queue operations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Literal, Protocol, cast

import fal_client
from dotenv import find_dotenv, load_dotenv

JobState = Literal["IN_QUEUE", "IN_PROGRESS", "COMPLETED"]


@dataclass(frozen=True)
class SubmitHandle:
    """Queue submit response metadata for one fal request."""

    request_id: str
    response_url: str
    status_url: str
    cancel_url: str


@dataclass(frozen=True)
class JobStatus:
    """Normalized queue status for one fal request."""

    state: JobState
    queue_position: int | None = None
    logs: list[dict[str, Any]] | None = None
    metrics: dict[str, Any] | None = None
    error: str | None = None
    error_type: str | None = None


class FalClient(Protocol):
    """Async fal queue adapter used by the core primitives.

    All operations are coroutines so the CLI layer can drive concurrent submits
    through ``asyncio.Semaphore(max_concurrency)`` without holding the GIL on
    blocking HTTP calls.
    """

    async def submit(
        self,
        app_id: str,
        arguments: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
    ) -> object: ...

    async def status(self, app_id: str, request_id: str) -> object: ...

    async def result(self, app_id: str, request_id: str) -> dict[str, Any]: ...

    async def cancel(self, app_id: str, request_id: str) -> None: ...


class _SubmitHandleLike(Protocol):
    request_id: str
    response_url: str
    status_url: str
    cancel_url: str


class _JobStatusLike(Protocol):
    state: JobState
    queue_position: int | None
    logs: list[dict[str, Any]] | None
    metrics: dict[str, Any] | None
    error: str | None
    error_type: str | None


def _normalize_fal_status(raw: object) -> SimpleNamespace:
    """Convert fal_client Queued/InProgress/Completed into a _JobStatusLike shape.

    fal_client.status returns one of three dataclasses whose class name encodes
    the state. This adapter flattens
    them into a single namespace with the fields that :class:`JobStatus`
    expects, so the core primitives can stay Fake-agnostic.
    """
    cls_name = type(raw).__name__
    if cls_name == "Queued":
        return SimpleNamespace(
            state="IN_QUEUE",
            queue_position=getattr(raw, "position", None),
            logs=None,
            metrics=None,
            error=None,
            error_type=None,
        )
    if cls_name == "InProgress":
        return SimpleNamespace(
            state="IN_PROGRESS",
            queue_position=None,
            logs=getattr(raw, "logs", None),
            metrics=None,
            error=None,
            error_type=None,
        )
    if cls_name == "Completed":
        return SimpleNamespace(
            state="COMPLETED",
            queue_position=None,
            logs=getattr(raw, "logs", None),
            metrics=getattr(raw, "metrics", None),
            error=getattr(raw, "error", None),
            error_type=getattr(raw, "error_type", None),
        )
    raise RuntimeError(f"Unknown fal_client status type: {cls_name}")


@dataclass(frozen=True)
class _DefaultFalClient:
    async def submit(
        self,
        app_id: str,
        arguments: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
    ) -> object:
        return await fal_client.submit_async(app_id, arguments=arguments, headers=headers or {})

    async def status(self, app_id: str, request_id: str) -> object:
        raw = await fal_client.status_async(app_id, request_id)
        return _normalize_fal_status(raw)

    async def result(self, app_id: str, request_id: str) -> dict[str, Any]:
        result = await fal_client.result_async(app_id, request_id)
        return dict(result)

    async def cancel(self, app_id: str, request_id: str) -> None:
        await fal_client.cancel_async(app_id, request_id)


async def submit(
    app_id: str,
    parameters: dict[str, Any],
    *,
    client: FalClient,
    headers: dict[str, str] | None = None,
) -> SubmitHandle:
    """Submit one request and return the queue handle for that iteration.

    This primitive is CLI-agnostic and stateless: it only forwards ``app_id``
    and ``parameters`` to the injected async ``client`` and returns normalized
    queue metadata. Concurrent calls are safe because core keeps no global
    state between coroutines.
    """
    handle = cast(_SubmitHandleLike, await client.submit(app_id, dict(parameters), headers=headers))
    return SubmitHandle(
        request_id=handle.request_id,
        response_url=handle.response_url,
        status_url=handle.status_url,
        cancel_url=handle.cancel_url,
    )


async def fetch_status(app_id: str, request_id: str, *, client: FalClient) -> JobStatus:
    """Fetch one request status and normalize it into :class:`JobStatus`.

    The returned object is a transport-neutral projection of fal queue states so
    CLI, FastAPI, and direct Python callers can share the same core contract.
    """
    status = cast(_JobStatusLike, await client.status(app_id, request_id))
    return JobStatus(
        state=status.state,
        queue_position=status.queue_position,
        logs=status.logs,
        metrics=status.metrics,
        error=status.error,
        error_type=status.error_type,
    )


async def fetch_result(app_id: str, request_id: str, *, client: FalClient) -> dict[str, Any]:
    """Fetch the raw fal result payload for one completed request.

    This core primitive stays stateless and returns the provider payload
    unchanged so higher layers can decide how to persist YAML updates and result
    files.
    """
    return await client.result(app_id, request_id)


async def cancel(app_id: str, request_id: str, *, client: FalClient) -> None:
    """Cancel one submitted request through the injected fal client.

    This primitive performs no YAML bookkeeping and keeps no cross-call state;
    higher layers remain responsible for orchestration and persistence.
    """
    await client.cancel(app_id, request_id)


def ensure_fal_key() -> None:
    if os.getenv("FAL_KEY"):
        return
    load_dotenv()
    if os.getenv("FAL_KEY"):
        return
    cwd_dotenv = find_dotenv(usecwd=True)
    if cwd_dotenv:
        load_dotenv(cwd_dotenv)


def default_fal_client() -> FalClient:
    """Create a fresh default fal client after validating ``FAL_KEY``.

    The factory performs environment loading on each call and returns a new
    adapter instance rather than reusing cached global state.
    """
    ensure_fal_key()
    if not os.getenv("FAL_KEY"):
        raise RuntimeError(
            "FAL_KEY environment variable is required. Set it in your shell environment "
            "(for example, in ~/.zshenv) before running falx online commands."
        )
    return _DefaultFalClient()

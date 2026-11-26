from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Any

import pytest

import falx.core as core_module
from falx.core import (
    JobStatus,
    SubmitHandle,
    cancel,
    default_fal_client,
    fetch_result,
    fetch_status,
    submit,
)
from tests.conftest import FakeFalClient, FalAPIError


@pytest.mark.anyio
async def test_submit_returns_handle_and_records_call(fal_client: FakeFalClient) -> None:
    parameters = {"prompt": "night city", "steps": 28}

    handle = await submit("fal-ai/flux/schnell", parameters, client=fal_client)

    assert handle == SubmitHandle(
        request_id="req-0001",
        response_url="https://queue.fal.run/fal-ai/flux/schnell/requests/req-0001",
        status_url="https://queue.fal.run/fal-ai/flux/schnell/requests/req-0001/status",
        cancel_url="https://queue.fal.run/fal-ai/flux/schnell/requests/req-0001/cancel",
    )
    assert fal_client.submit_calls == [("fal-ai/flux/schnell", parameters, None)]


@pytest.mark.anyio
async def test_submit_forwards_headers_to_queue_client(fal_client: FakeFalClient) -> None:
    parameters = {"prompt": "night city"}
    headers = {"X-Fal-Object-Lifecycle-Preference": '{"expiration_duration_seconds":3600}'}

    await submit("fal-ai/flux/schnell", parameters, client=fal_client, headers=headers)

    assert fal_client.submit_calls == [("fal-ai/flux/schnell", parameters, headers)]


def test_submit_handle_is_frozen() -> None:
    handle = SubmitHandle(
        request_id="req-1234",
        response_url="https://queue.fal.run/app/requests/req-1234",
        status_url="https://queue.fal.run/app/requests/req-1234/status",
        cancel_url="https://queue.fal.run/app/requests/req-1234/cancel",
    )

    with pytest.raises(FrozenInstanceError):
        handle.request_id = "req-9999"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("programmed", "expected"),
    [
        (
            JobStatus(state="IN_QUEUE", queue_position=3),
            JobStatus(state="IN_QUEUE", queue_position=3),
        ),
        (
            JobStatus(
                state="IN_PROGRESS",
                logs=[{"message": "starting"}],
            ),
            JobStatus(
                state="IN_PROGRESS",
                logs=[{"message": "starting"}],
            ),
        ),
        (
            JobStatus(
                state="COMPLETED",
                metrics={"duration": 1.2},
            ),
            JobStatus(
                state="COMPLETED",
                metrics={"duration": 1.2},
            ),
        ),
        (
            JobStatus(
                state="COMPLETED",
                error="model crashed",
                error_type="runtime_error",
                metrics={"duration": 0.4},
            ),
            JobStatus(
                state="COMPLETED",
                error="model crashed",
                error_type="runtime_error",
                metrics={"duration": 0.4},
            ),
        ),
    ],
)
@pytest.mark.anyio
async def test_fetch_status_returns_programmed_job_state(
    fal_client: FakeFalClient,
    programmed: Any,
    expected: JobStatus,
) -> None:
    fal_client.program_status("req-1234", programmed)

    status = await fetch_status("fal-ai/flux/schnell", "req-1234", client=fal_client)

    assert status == expected
    assert fal_client.status_calls == [("fal-ai/flux/schnell", "req-1234")]


def test_job_status_is_frozen() -> None:
    status = JobStatus(state="IN_QUEUE", queue_position=1)

    with pytest.raises(FrozenInstanceError):
        status.state = "COMPLETED"  # type: ignore[misc]


@pytest.mark.anyio
async def test_fetch_result_returns_result_dict(fal_client: FakeFalClient) -> None:
    result = {"images": [{"url": "https://cdn.example/image.png"}]}
    fal_client.program_result("req-1234", result)

    fetched = await fetch_result("fal-ai/flux/schnell", "req-1234", client=fal_client)

    assert fetched == result
    assert fal_client.result_calls == [("fal-ai/flux/schnell", "req-1234")]


@pytest.mark.anyio
async def test_cancel_delegates_to_client(fal_client: FakeFalClient) -> None:
    await cancel("fal-ai/flux/schnell", "req-1234", client=fal_client)

    assert fal_client.cancel_calls == [("fal-ai/flux/schnell", "req-1234")]


@pytest.mark.parametrize(
    ("call", "expected_message"),
    [
        (
            lambda client: submit("fal-ai/flux/schnell", {"prompt": "x"}, client=client),
            "submit exploded",
        ),
        (
            lambda client: fetch_status("fal-ai/flux/schnell", "req-1234", client=client),
            "status exploded",
        ),
        (
            lambda client: fetch_result("fal-ai/flux/schnell", "req-1234", client=client),
            "result exploded",
        ),
        (
            lambda client: cancel("fal-ai/flux/schnell", "req-1234", client=client),
            "cancel exploded",
        ),
    ],
)
@pytest.mark.anyio
async def test_core_api_propagates_fal_errors_unchanged(
    fal_client: FakeFalClient,
    call: Any,
    expected_message: str,
) -> None:
    if expected_message == "submit exploded":
        fal_client.program_submit(FalAPIError(503, expected_message, "temporary_unavailable"))
    elif expected_message == "status exploded":
        fal_client.program_status(
            "req-1234",
            FalAPIError(429, expected_message, "rate_limit"),
        )
    elif expected_message == "result exploded":
        fal_client.program_result(
            "req-1234",
            FalAPIError(500, expected_message, "server_error"),
        )
    else:
        fal_client.program_cancel(FalAPIError(409, expected_message, "already_done"))

    with pytest.raises(FalAPIError) as exc_info:
        await call(fal_client)

    assert exc_info.value.detail == expected_message


def test_default_fal_client_requires_fal_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.delenv("FAL_KEY_ID", raising=False)
    monkeypatch.delenv("FAL_KEY_SECRET", raising=False)
    monkeypatch.setattr(core_module, "load_dotenv", lambda *a, **kw: None)

    with pytest.raises(RuntimeError, match="FAL_KEY"):
        default_fal_client()


def test_normalize_queued_status_exposes_state_and_queue_position() -> None:
    from fal_client.client import Queued

    normalized = core_module._normalize_fal_status(Queued(position=3))

    assert normalized.state == "IN_QUEUE"
    assert normalized.queue_position == 3
    assert normalized.logs is None
    assert normalized.error is None


def test_normalize_in_progress_status_carries_logs() -> None:
    from fal_client.client import InProgress

    logs = [{"message": "loading model"}]
    normalized = core_module._normalize_fal_status(InProgress(logs=logs))

    assert normalized.state == "IN_PROGRESS"
    assert normalized.queue_position is None
    assert normalized.logs == logs
    assert normalized.error is None


def test_normalize_completed_status_exposes_error_fields() -> None:
    from fal_client.client import Completed

    raw = Completed(
        logs=[{"message": "done"}],
        metrics={"inference_time": 0.5},
        error="tensor mismatch",
        error_type="INFERENCE_ERROR",
    )

    normalized = core_module._normalize_fal_status(raw)

    assert normalized.state == "COMPLETED"
    assert normalized.metrics == {"inference_time": 0.5}
    assert normalized.error == "tensor mismatch"
    assert normalized.error_type == "INFERENCE_ERROR"


def test_normalize_unknown_status_type_raises() -> None:
    class _Unexpected:
        pass

    with pytest.raises(RuntimeError, match="Unknown fal_client status type"):
        core_module._normalize_fal_status(_Unexpected())

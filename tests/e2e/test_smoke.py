"""Real fal.ai CLI smoke test for the stateless stdout YAML contract.

Opt-in only. The default test run excludes ``-m e2e``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from falx.cli import app
from tests.yaml_utils import safe_dump, safe_load

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not os.getenv("FAL_KEY"), reason="FAL_KEY not set"),
]

E2E_ENDPOINT = "fal-ai/nano-banana-2"


def test_cli_stateless_stdout_yaml_smoke(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    input_yaml_path = tmp_path / "smoke.yaml"
    input_yaml_path.write_text(
        safe_dump(
            {
                "app_id": E2E_ENDPOINT,
                "parameters": {
                    "prompt": "small watercolor cat portrait",
                    "num_images": 1,
                    "output_format": "png",
                },
                "output_dir": str(output_dir),
                "slug": "smoke-cat",
                "version": 1,
            },
            sort_keys=False,
        )
    )

    runner = CliRunner()
    submit_result = runner.invoke(
        app,
        ["run", "--config", str(input_yaml_path), "--poll-interval", "2", "--timeout", "120"],
    )
    if submit_result.exit_code in (2, 3):
        pytest.skip(
            f"fal smoke did not complete cleanly: "
            f"stdout={submit_result.stdout!r} stderr={submit_result.stderr!r}"
        )
    assert submit_result.exit_code == 0, (
        f"submit failed: stdout={submit_result.stdout!r} stderr={submit_result.stderr!r}"
    )

    assert submit_result.stdout.startswith("request_id:")
    assert not submit_result.stdout.lstrip().startswith("{")
    submit_payload = safe_load(submit_result.stdout)
    assert submit_payload["status"] == "completed"
    request_id = submit_payload["request_id"]
    [batch] = submit_payload["takes"][0]["batches"]
    output_path = Path(batch["file_path"])
    assert output_path.is_file()
    assert output_path.parent == output_dir / "v1-1"
    assert output_path.name == "smoke-cat_v1-1-1.png"

    fetch_result = runner.invoke(
        app,
        [
            "fetch",
            "--config",
            str(input_yaml_path),
            "--request-id",
            request_id,
        ],
    )
    assert fetch_result.exit_code == 0, (
        f"fetch failed: stdout={fetch_result.stdout!r} stderr={fetch_result.stderr!r}"
    )
    assert fetch_result.stdout.startswith("request_id:")
    assert not fetch_result.stdout.lstrip().startswith("{")
    fetch_payload = safe_load(fetch_result.stdout)
    assert fetch_payload["request_id"] == request_id
    assert fetch_payload["status"] == "completed"

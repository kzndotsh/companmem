from __future__ import annotations

import json
from pathlib import Path

from companmem_pipeline.log import PipelineLogger, emit_console


def test_emit_console_redacts_api_key(capsys) -> None:
    emit_console(
        "test",
        "mem0",
        "info",
        "demo",
        api_key="secret-value",
        converter="origin_markdown",
    )
    err = capsys.readouterr().err
    assert "demo" in err
    assert "origin_markdown" in err
    assert "secret-value" not in err


def test_pipeline_logger_writes_jsonl_and_echoes(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr("companmem_pipeline.log.LOGS_DIR", tmp_path)
    with PipelineLogger("harvest", source="mem0", force=False) as log:
        log.info("docs_kept", url="https://example.com/docs", converter="origin_markdown")
        log.warn("docs_fetch_failed", url="https://example.com/missing")
        path = log.log_path
    err = capsys.readouterr().err
    assert "log_file" in err
    assert "docs_kept" in err
    assert "docs_fetch_failed" in err
    assert path.exists()
    lines = path.read_text(encoding="utf-8").splitlines()
    assert any('"event": "docs_kept"' in line for line in lines)
    assert any('"event": "run_completed"' in line for line in lines)


def test_logger_source_kwarg_does_not_collide(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("companmem_pipeline.log.LOGS_DIR", tmp_path)
    log = PipelineLogger("harvest", source="graphiti")
    try:
        log.info("search_hit", source="brave", url="https://example.com")
        line = log.log_path.read_text(encoding="utf-8").splitlines()[-1]
        row = json.loads(line)
        assert row["source"] == "graphiti"
        assert row["hit_source"] == "brave"
        assert row["url"] == "https://example.com"
    finally:
        log.close()

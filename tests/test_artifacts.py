"""Unit tests for harness.artifacts."""

from __future__ import annotations

from pathlib import Path

import pytest

from harness.artifacts import ArtifactMissing, Artifacts


def test_reply_raises_before_write(tmp_path: Path) -> None:
    a = Artifacts(tmp_path / "out")
    with pytest.raises(ArtifactMissing):
        a.reply()


def test_export_raises_before_write(tmp_path: Path) -> None:
    a = Artifacts(tmp_path / "out")
    with pytest.raises(ArtifactMissing):
        a.export()


def test_write_reply_then_read(tmp_path: Path) -> None:
    a = Artifacts(tmp_path / "out")
    a.write_reply("Hello, world!")
    assert a.reply() == "Hello, world!"


def test_write_export_then_read(tmp_path: Path) -> None:
    a = Artifacts(tmp_path / "out")
    data = {"key": "value", "num": 42}
    a.write_export(data)
    assert a.export() == data


def test_output_dir_created_on_write(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "deep" / "out"
    assert not out.exists()
    a = Artifacts(out)
    a.write_reply("text")
    assert out.is_dir()


def test_reply_reads_from_disk(tmp_path: Path) -> None:
    """reply() must work on a fresh Artifacts instance over the same directory."""
    out = tmp_path / "out"
    a1 = Artifacts(out)
    a1.write_reply("persisted text")

    a2 = Artifacts(out)  # new instance, same dir
    assert a2.reply() == "persisted text"


def test_export_reads_from_disk(tmp_path: Path) -> None:
    """export() must work on a fresh Artifacts instance over the same directory."""
    out = tmp_path / "out"
    a1 = Artifacts(out)
    a1.write_export({"x": 1})

    a2 = Artifacts(out)
    assert a2.export() == {"x": 1}


def test_output_dir_property(tmp_path: Path) -> None:
    out = tmp_path / "out"
    a = Artifacts(out)
    assert a.output_dir == out

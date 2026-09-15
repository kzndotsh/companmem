from __future__ import annotations

from companmem_pipeline.httputil import spa_prose_host


def test_spa_prose_host_kindroid() -> None:
    assert spa_prose_host("https://kindroid.ai/v2/docs/memory")
    assert spa_prose_host("https://www.kindroid.ai/v2/docs/memory/")
    assert not spa_prose_host("https://docs.mem0.ai/introduction")

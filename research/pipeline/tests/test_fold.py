from __future__ import annotations

from companmem_pipeline.fold import (
    dedupe_near_duplicate_summaries,
    build_contested_rows,
    filter_ledger_rows,
    is_weak_wiki_index_ledger,
    filter_summary_items,
    filter_unknown_items,
    fold_pages,
    is_documented_capability_unknown,
    is_near_duplicate_summary,
    is_peripheral_mechanism,
    is_self_referential_summary,
    mentions_add_search_loop,
    should_drop_ledger_row,
    unknown_superseded_by_docs,
    unknown_superseded_by_ledger,
)
from companmem_pipeline.lint import lint_audit


def _manifest() -> dict[str, object]:
    return {
        "id": "mem0",
        "name": "Mem0",
        "repo": "https://github.com/mem0ai/mem0",
        "docs": "https://docs.mem0.ai/llms.txt",
        "license": "Apache-2.0",
        "version_or_commit": "abc123",
        "observed_at": "2026-09-11",
        "pages": [
            {
                "url": "https://docs.mem0.ai/llms.txt",
                "kind": "docs",
                "accessed_at": "2026-09-11",
                "quality": "high",
            }
        ],
    }


def test_fold_skips_repo_hint_when_clone_skipped() -> None:
    manifest = {
        **_manifest(),
        "repo": None,
        "clone_skipped": True,
        "pages": [],
    }
    extracts = [
        {
            "identity_hints": {
                "repo": "https://github.com/getzep/zep",
            },
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [],
        }
    ]
    audit = fold_pages(extracts, manifest)
    assert audit["identity"]["repo"] is None


def test_fold_prefers_longer_quote_and_drops_uncited() -> None:
    extracts = [
        {
            "identity_hints": {"name": "", "repo": None, "docs": None, "license": None},
            "claimed_purpose": [{"text": "Store user memories", "quote": "Mem0", "locator": "h1"}],
            "mechanisms": [],
            "ledger": [
                {
                    "claim": "extracts memories",
                    "kind": "docs",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "quote": "short",
                    "locator": "how-it-works",
                    "confidence": "medium",
                    "label": "measured",
                },
                {
                    "claim": "no citation",
                    "kind": "docs",
                    "url": "",
                    "quote": "guess",
                    "locator": "",
                    "confidence": "unknown",
                    "label": "inferred",
                },
            ],
            "unknowns": [],
        },
        {
            "identity_hints": {"name": "Mem0", "repo": None, "docs": None, "license": None},
            "claimed_purpose": [],
            "mechanisms": [
                {
                    "text": "extracts memories",
                    "quote": "Mem0 extracts memories from the conversation",
                    "locator": "how-it-works",
                }
            ],
            "ledger": [
                {
                    "claim": "extracts memories",
                    "kind": "docs",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "quote": "Mem0 extracts memories from the conversation",
                    "locator": "how-it-works",
                    "confidence": "high",
                    "label": "measured",
                }
            ],
            "unknowns": [
                {
                    "text": "Dream internals not on this page",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "kind": "docs",
                }
            ],
        },
    ]
    audit = fold_pages(extracts, _manifest())
    assert audit["copy"] == []
    assert audit["refuse"] == []
    assert audit["consensus"] == []
    assert audit["contested"] == []
    assert len(audit["ledger"]) == 1
    row = audit["ledger"][0]
    assert "Mem0 extracts memories" in str(row["quote"])
    assert audit["identity"]["name"] == "Mem0"
    assert audit["identity"]["license"] == "Apache-2.0"
    assert audit["identity"]["version_or_commit"] == "abc123"
    assert audit["sources"][0]["url"] == "https://docs.mem0.ai/llms.txt"
    assert audit["mechanisms"] == [{"text": "extracts memories"}]
    assert audit["unknowns"] == []
    assert lint_audit(audit) == []


def test_fold_identity_hints_only_fill_empty() -> None:
    manifest = _manifest()
    manifest["license"] = None
    extracts = [
        {
            "identity_hints": {
                "name": "ShouldNotReplace",
                "repo": None,
                "docs": None,
                "license": "MIT",
                "version_or_commit": None,
            },
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [],
        }
    ]
    audit = fold_pages(extracts, manifest)
    assert audit["identity"]["name"] == "Mem0"
    assert audit["identity"]["license"] == "MIT"


def test_fold_unknowns_keep_page_url() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [
                {
                    "text": "No memory mechanisms on this page",
                    "url": "https://example.com/blog",
                    "kind": "blog",
                },
                {
                    "text": "No memory mechanisms on this page",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "kind": "docs",
                },
            ],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    urls = {str(row.get("url")) for row in audit["unknowns"]}
    assert urls == {"https://example.com/blog", "https://docs.mem0.ai/llms.txt"}
    assert lint_audit(audit) == []


def test_fold_drops_single_url_this_file_absence() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [
                {
                    "text": "Forget / deletion behavior: no tool is present in this file",
                    "url": "https://github.com/plastic-labs/honcho/blob/main/src/crud.py",
                    "kind": "code",
                },
                {
                    "text": "The forget/delete path is not defined in this file",
                    "url": "https://github.com/plastic-labs/honcho/blob/main/src/router.py",
                    "kind": "code",
                },
                {
                    "text": "Contradiction resolution is not implemented",
                    "url": "https://github.com/plastic-labs/honcho/issues/403",
                    "kind": "issue",
                },
            ],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    texts = {str(row.get("text")) for row in audit["unknowns"]}
    assert "The forget/delete path is not defined in this file" not in texts
    assert "Forget / deletion behavior: no tool is present in this file" not in texts
    assert "Contradiction resolution is not implemented" in texts


def test_fold_keeps_this_file_absence_on_two_urls() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [
                {
                    "text": "Forget is not present in this file",
                    "url": "https://github.com/plastic-labs/honcho/blob/main/src/a.py",
                    "kind": "code",
                },
                {
                    "text": "Forget is not present in this file",
                    "url": "https://github.com/plastic-labs/honcho/blob/main/src/b.py",
                    "kind": "code",
                },
            ],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    urls = {str(row.get("url")) for row in audit["unknowns"]}
    assert urls == {
        "https://github.com/plastic-labs/honcho/blob/main/src/a.py",
        "https://github.com/plastic-labs/honcho/blob/main/src/b.py",
    }


def test_is_near_duplicate_summary_merges_rephrased_purpose() -> None:
    left = "EverOS is a memory operating system for LLM agents with persistent structured memory"
    right = "EverOS memory operating system for LLM agents with persistent structured memory across sessions"
    assert is_near_duplicate_summary(left, right)
    assert not is_near_duplicate_summary(left, "Vector database for document retrieval only")


def test_dedupe_near_duplicate_summaries_keeps_longest() -> None:
    items = [
        {"text": "EverOS memory operating system for agents"},
        {
            "text": "EverOS is a memory operating system for LLM agents with persistent structured memory",
        },
    ]
    kept = dedupe_near_duplicate_summaries(items)
    assert len(kept) == 1
    assert "persistent structured memory" in kept[0]["text"]


def test_fold_dedupes_near_duplicate_claimed_purpose() -> None:
    ledger = [
        {
            "claim": "EverOS is a memory operating system for LLM agents",
            "kind": "docs",
            "url": "https://docs.evermind.ai/llms.txt",
            "quote": "EverOS is the Memory Operating System for Agentic AI",
            "locator": "intro",
            "confidence": "high",
            "label": "measured",
        }
    ]
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [
                {
                    "text": "EverOS is a memory operating system for LLM agents with persistent structured memory",
                    "quote": "EverOS is the Memory Operating System for Agentic AI",
                    "locator": "intro",
                },
                {
                    "text": "Memory operating system for agentic AI providing persistent structured memory across sessions",
                    "quote": "EverOS is the Memory Operating System for Agentic AI",
                    "locator": "intro",
                },
            ],
            "mechanisms": [],
            "ledger": ledger,
            "unknowns": [],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    assert len(audit["claimed_purpose"]) == 1


def test_fold_dedupes_unknowns_with_same_text_on_different_urls() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [
                {
                    "text": "Conflict resolution policy is not documented",
                    "url": "https://docs.evermind.ai/llms.txt",
                    "kind": "docs",
                },
                {
                    "text": "Conflict resolution policy is not documented",
                    "url": "https://docs.evermind.ai/cloud/overview",
                    "kind": "docs",
                },
            ],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    assert len(audit["unknowns"]) == 1


def test_is_near_duplicate_summary_matches_shared_parameter_name() -> None:
    left = (
        "Local search supports a conversation_history_max_turns setting, "
        "indicating per-session conversation history is tracked and bounded."
    )
    right = (
        "Local search uses a conversation_history_max_turns parameter, "
        "indicating the pipeline tracks some turn history for search context."
    )
    assert is_near_duplicate_summary(left, right)


def test_is_self_referential_summary_drops_circular_product_reference() -> None:
    text = (
        "GraphRAG uses hierarchical community detection to organize graph data, "
        "inspired by Microsoft's GraphRAG."
    )
    assert is_self_referential_summary(text, "microsoft-graphrag", "Microsoft GraphRAG")
    assert not is_self_referential_summary(
        text,
        "lightrag",
        "LightRAG",
    )


def test_mentions_add_search_loop_marks_integration_duplicates() -> None:
    left = "The integration pattern is retrieve-then-store: search() before answering, add() after."
    right = "Memory is written by calling add() after each turn and read by calling search() before responding."
    assert mentions_add_search_loop(left)
    assert is_near_duplicate_summary(left, right)


def test_filter_unknown_items_drops_documented_capabilities_and_piwheels() -> None:
    items = [
        {
            "text": "Forget / explicit deletion is available via MCP (delete_memory)",
            "url": "https://github.com/TeleAI-UAGI/telemem",
            "kind": "docs",
        },
        {
            "text": "Forget/deletion behavior from the memory store is not described",
            "url": "https://www.piwheels.org/project/telemem/",
            "kind": "blog",
        },
        {
            "text": "Conflict resolution policy is not described beyond similarity clustering",
            "url": "https://teleai-uagi.github.io/telemem/api/",
            "kind": "docs",
        },
    ]
    kept = filter_unknown_items(items)
    assert is_documented_capability_unknown(items[0]["text"])
    assert len(kept) == 1
    assert "Conflict resolution" in kept[0]["text"]


def test_filter_summary_items_drops_self_referential_rows() -> None:
    items = [
        {"text": "Inspired by Microsoft's GraphRAG community reports"},
        {"text": "Community reports are generated at multiple hierarchy levels"},
    ]
    kept = filter_summary_items(items, "microsoft-graphrag", "Microsoft GraphRAG")
    assert len(kept) == 1
    assert "hierarchy levels" in kept[0]["text"]


def test_is_weak_wiki_index_ledger() -> None:
    row = {
        "url": "https://wiki.nomi.ai/Category:FAQs",
        "quote": "How far back? / What is Backstory?",
    }
    assert is_weak_wiki_index_ledger(row)
    assert not is_weak_wiki_index_ledger(
        {
            "url": "https://wiki.nomi.ai/Mind_Map_2.0",
            "quote": "Mind Map entries can be edited by the user.",
        }
    )


def test_dedupe_ledger_near_duplicates_same_url() -> None:
    from companmem_pipeline.fold import dedupe_ledger_near_duplicates

    rows = [
        {
            "claim": "Memory is layered: a user-visible Memory tab plus a deeper automatic system.",
            "url": "https://help.replika.com/hc/en-us/articles/1",
            "quote": "short",
        },
        {
            "claim": "Memory is layered: a user-visible Memory tab plus a deeper automatic system derived from chat.",
            "url": "https://help.replika.com/hc/en-us/articles/1",
            "quote": "longer quote here",
        },
    ]
    out = dedupe_ledger_near_duplicates(rows)
    assert len(out) == 1
    assert out[0]["quote"] == "longer quote here"


def test_build_contested_rows_memory_edit() -> None:
    ledger = [
        {"quote": "The memories are out of your hands", "claim": "x"},
        {"quote": "edit their memories via mind mapping", "claim": "y"},
    ]
    rows = build_contested_rows(ledger)
    assert len(rows) == 1


def test_should_drop_ledger_row_moderation_and_context_only() -> None:
    moderation = {
        "claim": "Kindroid has a background moderation AI that monitors chats",
        "kind": "community",
        "url": "https://www.reddit.com/r/example/",
        "quote": "monitor",
    }
    assert should_drop_ledger_row(moderation, has_official_docs=False)
    blog_ctx = {
        "claim": "Kindroid memory is backed by LLM context window with no persistent store beyond it",
        "kind": "blog",
        "url": "https://blog.storychat.app/example",
        "quote": "tokens",
    }
    assert not should_drop_ledger_row(blog_ctx, has_official_docs=False)
    assert should_drop_ledger_row(blog_ctx, has_official_docs=True)
    docs_row = {
        "claim": "Long-term memory is infinite",
        "kind": "docs",
        "url": "https://kindroid.ai/v2/docs/memory/",
        "quote": "infinite",
    }
    assert not should_drop_ledger_row(docs_row, has_official_docs=True)


def test_unknown_superseded_by_docs() -> None:
    text = "No description on this page of how journal entries are stored, indexed, or retrieved"
    assert not unknown_superseded_by_docs(text, has_official_docs=False)
    assert unknown_superseded_by_docs(text, has_official_docs=True)


def test_filter_ledger_rows_drops_moderation() -> None:
    rows = [
        {
            "claim": "Flagging appeared sensitive enough to trigger on an AI-guessed age alone",
            "kind": "community",
            "url": "https://www.reddit.com/r/x/",
            "quote": "flagged",
        },
        {
            "claim": "Journal cap of three entries per message",
            "kind": "docs",
            "url": "https://kindroid.ai/v2/docs/memory/",
            "quote": "only 3",
        },
    ]
    kept = filter_ledger_rows(rows, has_official_docs=True)
    assert len(kept) == 1
    assert kept[0]["kind"] == "docs"


def test_is_peripheral_mechanism() -> None:
    assert is_peripheral_mechanism("A community plugin adds extra lorebook slots")
    assert is_peripheral_mechanism(
        "Start a new chat uses the Cohere API for reranking"
    )
    assert not is_peripheral_mechanism("HypaMemory v3 compresses conversation history")


def test_fold_canonicalizes_github_issue_urls() -> None:
    manifest = {
        **_manifest(),
        "id": "risuai",
        "name": "RisuAI",
        "repo": "https://github.com/kwaroran/Risuai",
    }
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [
                {
                    "claim": "lorebook",
                    "kind": "issue",
                    "url": "https://github.com/kwaroran/RisuAI/issues/205",
                    "quote": "lorebook entry",
                    "locator": "#issue",
                    "confidence": "medium",
                    "label": "measured",
                }
            ],
            "unknowns": [],
        }
    ]
    audit = fold_pages(extracts, manifest)
    assert audit["ledger"][0]["url"] == (
        "https://github.com/kwaroran/Risuai/issues/205"
    )


def test_fold_drops_uncited_mechanisms() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [{"text": "orphan purpose", "quote": "nope", "locator": ""}],
            "mechanisms": [{"text": "orphan mechanism", "quote": "nope", "locator": ""}],
            "ledger": [
                {
                    "claim": "extracts memories",
                    "kind": "docs",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "quote": "Mem0 extracts memories",
                    "locator": "how-it-works",
                    "confidence": "high",
                    "label": "measured",
                }
            ],
            "unknowns": [],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    assert audit["mechanisms"] == []
    assert audit["claimed_purpose"] == []
    assert len(audit["ledger"]) == 1


def test_should_drop_ledger_row_comparison_benchmark_blog_path() -> None:
    row = {
        "claim": "LangMem scored X",
        "kind": "blog",
        "url": "https://mem0.ai/blog/benchmarked-openai-memory-vs-langmem",
        "quote": "benchmark",
        "locator": "blog",
    }
    assert should_drop_ledger_row(row, has_official_docs=True)


def test_should_drop_ledger_row_competitor_compare_host() -> None:
    row = {
        "claim": "LangMem is self-hosted",
        "kind": "blog",
        "url": "https://www.graphlit.com/vs/langmem",
        "quote": "self-hosted",
        "locator": "compare",
    }
    assert should_drop_ledger_row(row, has_official_docs=True)


def test_unknown_superseded_by_ledger_store_shape_when_context_tree_documented() -> None:
    ledger = [
        {
            "claim": "Memory is organized as a context tree within a space, not a flat transcript log",
            "kind": "docs",
            "url": "https://docs.byterover.dev/v4/overview.md",
        }
    ]
    text = (
        "The page does not describe the internal structure of what is stored — "
        "whether spaces hold full transcript logs or curated facts"
    )
    assert unknown_superseded_by_ledger(text, ledger)


def test_unknown_superseded_by_ledger_worker_persist_when_sqlite_documented() -> None:
    ledger = [
        {
            "claim": "claude-mem uses SQLite as its persistent memory store, writing curated observations",
            "kind": "docs",
            "url": "https://docs.claude-mem.ai/architecture/database.md",
        }
    ]
    text = (
        "No documentation describes what the memory worker persists, "
        "how facts/summaries are written or updated"
    )
    assert unknown_superseded_by_ledger(text, ledger)


def test_should_drop_ledger_row_roadmap_spec_issue_claim() -> None:
    row = {
        "claim": "[plan-12] Provider roadmap — net-new capabilities, not defects",
        "kind": "issue",
        "url": "https://github.com/thedotmack/claude-mem/issues/2785",
        "quote": "net-new capabilities, not defects",
        "locator": "issue",
    }
    assert should_drop_ledger_row(row, has_official_docs=True)


def test_filter_unknown_items_drops_legacy_cipher_mcp_issue_unknown() -> None:
    items = [
        {
            "text": "The write path for MCP mode is not explained — Qdrant via claude.json",
            "url": "https://github.com/campfirein/byterover-cli/issues/263",
        }
    ]
    assert filter_unknown_items(items) == []


def test_filter_unknown_items_drops_bestaiweb_compare_host() -> None:
    items = [
        {
            "text": "ByteRover wins LoCoMo",
            "url": "https://www.bestaiweb.ai/byterover-mem0g-benchmark/",
        }
    ]
    assert filter_unknown_items(items) == []


def test_should_drop_ledger_row_hindsight_blog_index_when_official_docs() -> None:
    row = {
        "claim": "Hindsight blog lists posts",
        "kind": "blog",
        "url": "https://hindsight.vectorize.io/blog",
        "quote": "blog",
        "locator": "blog",
    }
    assert should_drop_ledger_row(row, has_official_docs=True)


def test_should_drop_ledger_row_vectorize_compare_article_when_official_docs() -> None:
    row = {
        "claim": "Hindsight beats Supermemory",
        "kind": "blog",
        "url": "https://vectorize.io/articles/hindsight-vs-supermemory",
        "quote": "vs",
        "locator": "article",
    }
    assert should_drop_ledger_row(row, has_official_docs=True)


def test_should_drop_ledger_row_devto_when_official_docs() -> None:
    row = {
        "claim": "Memobase uses profiles",
        "kind": "blog",
        "url": "https://dev.to/author/memobase-post",
        "quote": "profiles",
        "locator": "blog",
    }
    assert should_drop_ledger_row(row, has_official_docs=True)
    assert not should_drop_ledger_row(row, has_official_docs=False)


def test_unknown_superseded_by_ledger_merge_when_merge_py_documented() -> None:
    ledger = [
        {
            "claim": "Profile slot write path is LLM-driven merge of existing and incoming text",
            "kind": "code",
            "url": "https://github.com/memodb-io/memobase/blob/sha/merge.py",
        }
    ]
    text = "Conflict / supersession: no description of how contradictory profile updates are resolved"
    assert unknown_superseded_by_ledger(text, ledger)


def test_unknown_superseded_by_ledger_forget_when_code_documents_delete() -> None:
    ledger = [
        {
            "claim": "Forget is implemented via store.adelete on removed_ids",
            "kind": "code",
            "url": "https://github.com/example/repo/blob/sha/file.py",
        }
    ]
    text = "Forget / delete path: this README does not describe how memories are deleted"
    assert unknown_superseded_by_ledger(text, ledger)


def test_unknown_superseded_by_ledger_delete_document_when_documented() -> None:
    ledger = [
        {
            "claim": "Deleting a document removes its facts, links, and chunks within the bank",
            "kind": "code",
            "url": "https://github.com/vectorize-io/hindsight/blob/sha/README.md",
        }
    ]
    text = "Explicit delete-from-store API for individual memories is unclear whether facts can be deleted"
    assert unknown_superseded_by_ledger(text, ledger)


def test_unknown_superseded_by_ledger_isolation_when_bank_documented() -> None:
    ledger = [
        {
            "claim": "Bank isolation is enforced: two banks never see each other's rows",
            "kind": "code",
            "url": "https://github.com/vectorize-io/hindsight/blob/sha/README.md",
        }
    ]
    text = "Isolation model: no symbol indicates per-user, per-session, or per-agent scoping"
    assert unknown_superseded_by_ledger(text, ledger)


def test_filter_unknown_items_drops_meta_community_noise() -> None:
    items = [
        {
            "text": "No community discussion of continuity failures despite this being a community thread",
            "url": "https://news.ycombinator.com/item?id=1",
        }
    ]
    assert filter_unknown_items(items) == []

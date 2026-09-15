from __future__ import annotations

from pathlib import Path

from companmem_pipeline.harvest import (
    ISSUE_NOISE_RE,
    ISSUE_UX_RE,
    LOGIN_PATH_RE,
    SEARCH_CAP,
    allowed_source_url,
    blog_seed_urls,
    body_markers_match,
    community_confirm_queries,
    detect_license,
    docs_host_path_prefix,
    first_party_hosts,
    github_owner_repo,
    is_community_host,
    is_community_thread,
    is_generic_code_name,
    is_generic_docs_url,
    is_marketing_home,
    is_memory_path,
    is_noisy_issue,
    is_search_url,
    issue_sort_key,
    load_seed,
    parse_llms_links,
    parse_robots_sitemaps,
    parse_sitemap_locs,
    product_ids,
    product_mentioned,
    product_named_in_url_or_title,
    product_path_tokens,
    public_https_repo,
    search_page_meta,
    search_queries,
    search_url_skip_reason,
    sibling_on_shared_host,
    select_code_files,
    select_code_inventory,
    select_docs_urls,
    select_listed_code_files,
    select_search_urls,
)


def test_github_owner_repo_https_and_ssh() -> None:
    assert github_owner_repo("https://github.com/mem0ai/mem0") == ("mem0ai", "mem0")
    assert github_owner_repo("https://github.com/mem0ai/mem0.git") == ("mem0ai", "mem0")
    assert github_owner_repo("ssh://git@github.com/mem0ai/mem0") == ("mem0ai", "mem0")
    assert github_owner_repo("git@github.com:letta-ai/letta-code.git") == (
        "letta-ai",
        "letta-code",
    )
    assert github_owner_repo("") is None


def test_seed_has_inclusion_lists() -> None:
    seed = load_seed()
    assert "slices" not in seed
    ids = product_ids()
    assert "mem0" in ids
    assert "claude-mem" in ids
    products = seed["products"]
    assert isinstance(products, dict)
    for slug in ids:
        product = products[slug]
        assert "slice" not in product
        assert isinstance(product.get("open_code"), list), slug
        assert isinstance(product.get("open_docs"), list), slug
        assert all(isinstance(item, str) for item in product["open_code"]), slug
        assert all(isinstance(item, str) for item in product["open_docs"]), slug
        if not product.get("clone"):
            assert product["open_code"] == []


def test_letta_seed_skips_legacy_memory_blocks() -> None:
    letta = load_seed()["products"]["letta"]
    prefixes = list(letta["skip_url_prefixes"])
    assert any("memfs" in url for url in letta["open_docs"])
    assert any("agent-sdk/memory" in url for url in letta["open_docs"])
    assert search_url_skip_reason(
        "https://docs.letta.com/v1-sdk/memory/memory-blocks",
        prefixes,
    ) == "skip_prefix"
    assert search_url_skip_reason(
        "https://www.letta.com/blog/memory-blocks/",
        prefixes,
    ) == "skip_prefix"
    assert search_url_skip_reason(
        "https://www.letta.com/constitution/",
        prefixes,
    ) == "skip_prefix"
    assert search_url_skip_reason(
        "https://docs.letta.com/concepts/memfs/index.md",
        prefixes,
    ) is None


def test_blog_seed_skips_github_forge() -> None:
    urls = blog_seed_urls(
        {
            "repo": "https://github.com/coleam00/mcp-mem0",
            "docs": "https://github.com/coleam00/mcp-mem0/blob/main/README.md",
            "census_sources": [],
            "skip_url_prefixes": [],
        }
    )
    assert urls == []
    urls = blog_seed_urls(
        {
            "repo": "https://github.com/mem0ai/mem0",
            "docs": "https://docs.mem0.ai/llms.txt",
            "census_sources": [],
            "skip_url_prefixes": [],
        }
    )
    assert urls == ["https://mem0.ai/blog", "https://blog.mem0.ai/"]


def test_detect_license_agpl_before_gpl(tmp_path: Path) -> None:
    (tmp_path / "LICENSE").write_text(
        "GNU AFFERO GENERAL PUBLIC LICENSE\nVersion 3, 19 November 2007\n"
        "This is a GNU General Public License version 3 derived text.\n",
        encoding="utf-8",
    )
    assert detect_license(tmp_path) == "AGPL-3.0"


def test_select_code_files_prefers_src_over_nested_readme(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Honcho\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("GNU AFFERO GENERAL PUBLIC LICENSE\n", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "memory.py").write_text("def remember():\n    pass\n", encoding="utf-8")
    (src / "deriver.py").write_text("def derive():\n    pass\n", encoding="utf-8")
    nested = tmp_path / "docs" / "v2"
    nested.mkdir(parents=True)
    (nested / "README.md").write_text("nested\n", encoding="utf-8")
    examples = tmp_path / "examples" / "crewai"
    examples.mkdir(parents=True)
    (examples / "README.md").write_text("example\n", encoding="utf-8")
    (examples / "memory.py").write_text("pass\n", encoding="utf-8")
    selected = [p.relative_to(tmp_path).as_posix() for p in select_code_files(tmp_path)]
    assert "README.md" in selected
    assert "LICENSE" not in selected
    assert "src/memory.py" in selected
    assert "src/models.py" not in selected
    assert "src/deriver.py" not in selected
    assert "docs/v2/README.md" not in selected
    assert "examples/crewai/README.md" not in selected
    assert "examples/crewai/memory.py" not in selected


def test_public_https_repo_from_ssh() -> None:
    assert (
        public_https_repo("ssh://git@github.com/plastic-labs/honcho", None)
        == "https://github.com/plastic-labs/honcho"
    )


def test_allowed_source_url_first_party_only() -> None:
    product = {
        "id": "honcho",
        "name": "Honcho",
        "repo": "https://github.com/plastic-labs/honcho",
        "docs": "https://honcho.dev/docs/llms.txt",
    }
    repo_meta = {"origin": "ssh://git@github.com/plastic-labs/honcho"}
    hosts = first_party_hosts(product, repo_meta)
    assert "docs.honcho.dev" in hosts
    assert "honcho.dev" in hosts
    assert "github.com" not in hosts
    assert allowed_source_url("https://docs.honcho.dev/v2/guides/architecture", product, repo_meta)
    assert allowed_source_url(
        "https://github.com/plastic-labs/honcho/blob/main/src/models.py",
        product,
        repo_meta,
    )
    assert not allowed_source_url(
        "https://docs.mem0.ai/openmemory/integrations",
        product,
        repo_meta,
    )
    assert not allowed_source_url("https://docs.openclaw.ai/concepts/memory", product, repo_meta)
    assert not allowed_source_url("https://discord.com/invite/honcho", product, repo_meta)
    assert not allowed_source_url("https://app.honcho.dev/login", product, repo_meta)
    assert not allowed_source_url(
        "https://github.com/coleam00/mcp-mem0/blob/main/README.md",
        product,
        repo_meta,
    )


def test_shared_docs_host_is_path_scoped() -> None:
    graphiti = {
        "id": "graphiti",
        "name": "Graphiti",
        "repo": "https://github.com/getzep/graphiti",
        "docs": "https://help.getzep.com/graphiti",
        "clone": True,
        "open_docs": ["https://help.getzep.com/graphiti/llms.txt"],
        "skip_url_prefixes": [],
    }
    repo_meta = {"origin": "https://github.com/getzep/graphiti"}
    assert docs_host_path_prefix(graphiti) == "/graphiti"
    assert allowed_source_url(
        "https://help.getzep.com/graphiti/working-with-data/searching.md",
        graphiti,
        repo_meta,
    )
    assert allowed_source_url("https://help.getzep.com/graphiti.md", graphiti, repo_meta)
    assert allowed_source_url(
        "https://www.getzep.com/platform/graphiti/",
        graphiti,
        repo_meta,
    )
    assert not allowed_source_url(
        "https://help.getzep.com/v2/sdk-reference/memory/delete.md",
        graphiti,
        repo_meta,
    )
    assert not allowed_source_url("https://help.getzep.com/eve.md", graphiti, repo_meta)
    assert sibling_on_shared_host(
        "https://help.getzep.com/v2/sdk-reference/memory/delete.md",
        graphiti,
        repo_meta,
    )
    kept, _ = select_search_urls(
        [
            "https://help.getzep.com/graphiti/getting-started/overview.md",
            "https://help.getzep.com/v2/sdk-reference/memory/delete.md",
            "https://help.getzep.com/eve.md",
            "https://www.getzep.com/platform/graphiti/",
        ],
        graphiti,
        repo_meta,
        set(),
    )
    assert kept[0] == "https://help.getzep.com/graphiti/getting-started/overview.md"
    assert "https://www.getzep.com/platform/graphiti/" in kept
    assert "https://help.getzep.com/v2/sdk-reference/memory/delete.md" not in kept
    assert "https://help.getzep.com/eve.md" not in kept
    queries = search_queries(graphiti)
    assert any(q.startswith("site:help.getzep.com/graphiti") for q in queries)
    assert blog_seed_urls(graphiti) == []
    assert "https://blog.getzep.com/graphiti-knowledge-graphs-for-agents" in blog_seed_urls(
        {
            **graphiti,
            "census_sources": [
                "https://blog.getzep.com/graphiti-knowledge-graphs-for-agents"
            ],
        }
    )
    zep = {
        "id": "zep",
        "name": "Zep Cloud",
        "docs": "https://help.getzep.com/llms.txt",
        "repo": None,
        "skip_url_prefixes": [
            "https://github.com/getzep/graphiti",
            "https://help.getzep.com/graphiti",
            "https://help.getzep.com/v2",
            "https://www.getzep.com/",
            "https://getzep.com/",
        ],
    }
    assert docs_host_path_prefix(zep) is None
    assert allowed_source_url("https://help.getzep.com/eve.md", zep, {})
    prefixes = list(zep["skip_url_prefixes"])
    assert (
        search_url_skip_reason(
            "https://help.getzep.com/graphiti/getting-started/overview.md",
            prefixes,
        )
        == "skip_prefix"
    )
    assert (
        search_url_skip_reason(
            "https://help.getzep.com/v2/sdk-reference/memory/get.md",
            prefixes,
        )
        == "skip_prefix"
    )
    assert (
        search_url_skip_reason(
            "https://www.getzep.com/mem0-alternative/",
            prefixes,
        )
        == "skip_prefix"
    )


def test_select_code_files_skips_generic_meta(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# x\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# changes\n", encoding="utf-8")
    (tmp_path / "CONTRIBUTING.md").write_text("# contrib\n", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "memory.py").write_text("def remember():\n    pass\n", encoding="utf-8")
    selected = [p.relative_to(tmp_path).as_posix() for p in select_code_files(tmp_path)]
    assert selected == ["README.md", "src/memory.py"]


def test_select_code_scores_content_quota_and_package_root(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Honcho\nSee `src/main.py`\n", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("def main():\n    pass\n", encoding="utf-8")
    (src / "models.py").write_text("class Peer:\n    pass\n", encoding="utf-8")
    (src / "explore.py").write_text("def walk():\n    pass\n", encoding="utf-8")
    deriver = src / "deriver"
    deriver.mkdir()
    (deriver / "deriver.py").write_text("class Deriver:\n    pass\n", encoding="utf-8")
    for i in range(6):
        (deriver / f"worker_{i}.py").write_text(
            "def search_memory():\n    pass\n",
            encoding="utf-8",
        )
    (src / "embedding_client.py").write_text("def embed():\n    pass\n", encoding="utf-8")
    cli = tmp_path / "honcho-cli" / "src" / "honcho_cli"
    cli.mkdir(parents=True)
    for i in range(8):
        (cli / f"cmd_{i}.py").write_text("print('honcho memory')\n", encoding="utf-8")
    product = {"id": "honcho", "name": "Honcho"}
    inventory = select_code_inventory(tmp_path, product)
    names = [p.relative_to(tmp_path).as_posix() for p in inventory.files]
    assert "README.md" in names
    assert "src/main.py" in names
    assert "src/models.py" in names
    assert "src/deriver/deriver.py" in names
    assert "src/explore.py" not in names
    deriver_kept = [n for n in names if n.startswith("src/deriver/")]
    assert len(deriver_kept) <= 4
    assert "src/deriver/deriver.py" in deriver_kept
    cli_kept = [n for n in names if n.startswith("honcho-cli/")]
    assert len(cli_kept) <= 4
    assert inventory.signaled > len(inventory.files)
    reasons = {row["reason"] for row in inventory.skipped}
    assert reasons & {"quota", "cap"}
    assert "src/models.py" in inventory.must_open
    assert "src/main.py" in inventory.must_open
    assert inventory.skipped_total >= len(inventory.skipped)


def test_memory_path_uses_this_product_not_siblings(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# x\n", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "graphiti_client.py").write_text("pass\n", encoding="utf-8")
    (src / "mem0.py").write_text("pass\n", encoding="utf-8")
    (src / "memory.py").write_text("pass\n", encoding="utf-8")
    honcho = select_code_files(tmp_path, {"id": "honcho", "name": "Honcho"})
    names = [p.relative_to(tmp_path).as_posix() for p in honcho]
    assert "src/memory.py" in names
    assert "src/graphiti_client.py" not in names
    assert "src/mem0.py" not in names
    mem0 = select_code_files(tmp_path, {"id": "mem0", "name": "Mem0"})
    mem0_names = [p.relative_to(tmp_path).as_posix() for p in mem0]
    assert "src/mem0.py" in mem0_names
    assert "src/memory.py" in mem0_names


def test_parse_sitemap_and_robots() -> None:
    xml = """<?xml version="1.0"?>
    <urlset>
      <url><loc>https://honcho.dev/docs/memory</loc></url>
      <url><loc>https://honcho.dev/changelog</loc></url>
    </urlset>
    """
    assert parse_sitemap_locs(xml) == [
        "https://honcho.dev/docs/memory",
        "https://honcho.dev/changelog",
    ]
    robots = "User-agent: *\nSitemap: https://honcho.dev/sitemap.xml\n"
    assert parse_robots_sitemaps(robots) == ["https://honcho.dev/sitemap.xml"]


def test_generic_docs_and_github_chrome() -> None:
    assert is_generic_docs_url("https://github.com/plastic-labs/honcho")
    assert is_generic_docs_url("https://github.com/plastic-labs/honcho/tags")
    assert is_generic_docs_url("https://github.com/plastic-labs/honcho/issues")
    assert is_generic_docs_url("https://honcho.dev/changelog")
    assert not is_generic_docs_url(
        "https://github.com/plastic-labs/honcho/blob/main/src/models.py"
    )
    assert is_community_host("news.ycombinator.com")
    assert is_community_host("old.reddit.com")
    assert is_community_host("forum.honcho.dev")
    assert not is_community_host("docs.honcho.dev")


def test_search_lane_filters_without_filling_docs() -> None:
    mem0 = {
        "id": "mem0",
        "name": "Mem0",
        "docs": "https://docs.mem0.ai/llms.txt",
        "repo": "https://github.com/mem0ai/mem0",
        "clone": True,
        "open_docs": ["https://docs.mem0.ai/llms.txt"],
        "skip_url_prefixes": [],
    }
    repo_meta = {"origin": "https://github.com/mem0ai/mem0"}
    queries = search_queries(mem0)
    assert any("doesn't remember" in q for q in queries)
    assert any("LoCoMo" in q for q in queries)
    assert any(q.startswith("site:docs.mem0.ai") for q in queries)
    assert all("wikipedia" not in q.lower() for q in queries)
    assert all("reddit" not in q.lower() for q in queries)
    closed = search_queries(
        {"id": "replika", "name": "Replika", "clone": False, "docs": "https://help.replika.com/"}
    )
    assert any(q.startswith("site:en.wikipedia.org") for q in closed)
    assert is_search_url("https://docs.mem0.ai/platform/overview", [])
    assert search_url_skip_reason("https://mem0.ai/", [], skip_home=True) == "marketing_home"
    assert search_url_skip_reason("https://deepwiki.com/mem0ai/mem0", []) == "mirror"
    assert search_url_skip_reason("https://news.ycombinator.com/item?id=1", []) == (
        "community_host"
    )
    assert search_url_skip_reason("https://github.com/mem0ai/mem0/issues/1", []) == "forge"
    assert search_url_skip_reason("https://arxiv.org/abs/2401.0001", []) == "arxiv"
    assert is_search_url("https://example.com/mem0-forgets-names", [])
    already = {"https://docs.mem0.ai/llms.txt"}
    kept, truncated = select_search_urls(
        [
            "https://docs.mem0.ai/llms.txt",
            "https://mem0.ai/",
            "https://docs.mem0.ai/platform/overview",
            "https://news.ycombinator.com/item?id=1",
            "https://blog.example.com/mem0-review",
            "https://github.com/mem0ai/mem0",
            "https://deepwiki.com/mem0ai/mem0",
            "https://microsoft.github.io/autogen/0.2/docs/ecosystem/mem0/",
        ],
        mem0,
        repo_meta,
        already,
        cap=SEARCH_CAP,
    )
    assert "https://docs.mem0.ai/llms.txt" not in kept
    assert "https://mem0.ai/" not in kept
    assert kept[0] == "https://docs.mem0.ai/platform/overview"
    assert "https://blog.example.com/mem0-review" in kept
    assert "https://news.ycombinator.com/item?id=1" not in kept
    assert "https://deepwiki.com/mem0ai/mem0" not in kept
    assert not truncated
    assert search_page_meta("https://docs.mem0.ai/platform/overview", mem0, repo_meta) == (
        "docs",
        "high",
    )
    assert search_page_meta("https://blog.example.com/mem0-review", mem0, repo_meta) == (
        "blog",
        "medium",
    )
    home_kept, _ = select_search_urls(
        ["https://kindroid.ai/"],
        {
            "id": "kindroid",
            "name": "Kindroid",
            "clone": False,
            "open_docs": [],
            "docs": None,
            "skip_url_prefixes": [],
        },
        {},
        set(),
    )
    assert home_kept == ["https://kindroid.ai/"]


def test_issue_rank_prefers_ux_over_noise() -> None:
    bot = {
        "title": "Bump requests from 1.0 to 2.0",
        "user": {"login": "dependabot[bot]"},
        "body": "",
        "comments": 0,
    }
    ux = {
        "title": "Honcho doesn't remember my name across sessions",
        "user": {"login": "alice"},
        "body": "lost context after a day",
        "comments": 4,
        "reactions": {"total_count": 3},
    }
    tech = {
        "title": "TypeError in deriver worker",
        "user": {"login": "bob"},
        "body": "pytest stack trace on import error",
        "comments": 1,
        "reactions": {"total_count": 0},
    }
    assert is_noisy_issue(bot)
    assert not is_noisy_issue(ux)
    assert issue_sort_key(ux) < issue_sort_key(tech)
    assert ISSUE_UX_RE.search("please delete memory for this user")
    assert ISSUE_UX_RE.search("personalization is wrong")
    assert ISSUE_UX_RE.search("doesn’t remember me")
    assert ISSUE_UX_RE.search("character forgets my name")
    assert ISSUE_UX_RE.search("it forgot my name across sessions")
    assert ISSUE_UX_RE.search("doesn't know who I am")
    assert not ISSUE_UX_RE.search("does not know how to compile")
    assert not ISSUE_UX_RE.search("confused about docker install")
    assert not ISSUE_UX_RE.search("relationship between tables in postgres")
    assert not ISSUE_UX_RE.search("change my namespace")
    assert not ISSUE_UX_RE.search("personal access token")
    assert not ISSUE_NOISE_RE.search("Test: character forgets my name")
    assert ISSUE_NOISE_RE.search("test(deps): bump pytest")
    assert not LOGIN_PATH_RE.search("/api/v1/members")
    assert LOGIN_PATH_RE.search("/login")


def test_memory_path_boundaries_and_markdown_links() -> None:
    assert is_memory_path("src/memory.py")
    assert is_memory_path("src/vector_store/__init__.py")
    assert is_memory_path("src/embedding_client.py")
    assert not is_memory_path("src/explore.py")
    assert not is_memory_path("src/graphql_client.py")
    links = parse_llms_links(
        '[Peer card](https://honcho.dev/docs/peer-card "title")\n'
        "[rel](/docs/memory)\n"
        "[skip](#anchor)",
        "https://honcho.dev/docs/llms.txt",
    )
    assert "https://honcho.dev/docs/peer-card" in links
    assert "https://honcho.dev/docs/memory" in links
    assert all(not u.endswith("#anchor") for u in links)
    xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += "<url><loc>https://honcho.dev/docs/memory</loc></url></urlset>"
    assert parse_sitemap_locs(xml) == ["https://honcho.dev/docs/memory"]
    namespaced = "<urlset><url><sm:loc>https://honcho.dev/a</sm:loc></url></urlset>"
    assert parse_sitemap_locs(namespaced) == ["https://honcho.dev/a"]
    encoded = "<urlset><url><loc>https://honcho.dev/a&amp;b</loc></url></urlset>"
    assert parse_sitemap_locs(encoded) == ["https://honcho.dev/a&b"]
    links = parse_llms_links(
        "[img](https://honcho.dev/logo.png)\n[ok](https://honcho.dev/docs/memory)",
        "https://honcho.dev/docs/llms.txt",
    )
    assert links == ["https://honcho.dev/docs/memory"]
    zep_tokens = product_path_tokens({"id": "zep", "name": "Zep Cloud"})
    assert "zep" in zep_tokens
    assert "cloud" not in zep_tokens
    honcho = {"id": "honcho", "name": "Honcho"}
    assert product_mentioned("Honcho forgot my birthday", honcho)
    assert not product_mentioned("a lettable API", {"id": "letta", "name": "Letta"})
    assert is_generic_code_name("SECURITY.md")
    assert not is_generic_code_name("security.py")
    assert not is_generic_code_name("changes.py")
    assert is_generic_docs_url("https://github.com/plastic-labs/honcho/security")
    assert not is_generic_docs_url("https://docs.honcho.dev/docs/security")


def test_docs_rank_drops_old_version_and_collapses_api() -> None:
    honcho = {"id": "honcho", "name": "Honcho"}
    urls = [
        "https://honcho.dev/docs/llms-full.txt",
        "https://honcho.dev/docs/v3/documentation/introduction/overview",
        "https://honcho.dev/docs/v3/documentation/core-concepts/memory",
        "https://honcho.dev/docs/v3/api-reference/endpoint/peers/get-peers",
        "https://honcho.dev/docs/v3/api-reference/endpoint/peers/create-peer",
        "https://honcho.dev/docs/v1/api-reference/endpoint/apps/create-app",
        "https://honcho.dev/docs/v1/api-reference/endpoint/apps/get-app",
        "https://honcho.dev/docs/v1/api-reference/endpoint/collections/delete-collection",
        "https://honcho.dev/",
    ]
    picked = select_docs_urls(urls, honcho, skip_home=True)
    kept = picked.urls
    assert "https://honcho.dev/docs/llms-full.txt" in kept
    assert "https://honcho.dev/docs/v3/documentation/introduction/overview" in kept
    assert "https://honcho.dev/docs/v3/documentation/core-concepts/memory" in kept
    assert "https://honcho.dev/" not in kept
    assert all("/v1/" not in url for url in kept)
    assert "https://honcho.dev/docs/v3/api-reference/endpoint/peers/get-peers" in kept
    assert "https://honcho.dev/docs/v3/api-reference/endpoint/peers/create-peer" not in kept
    reasons = {row["reason"] for row in picked.skipped}
    assert "old_version" in reasons
    assert "api_collapse" in reasons
    assert is_marketing_home("https://honcho.dev/")
    assert not is_marketing_home(
        "https://honcho.dev/docs/v3/documentation/introduction/overview"
    )
    assert is_community_thread("https://news.ycombinator.com/item?id=47831013")
    assert not is_community_thread("https://x.com/honchodotdev")
    assert is_community_thread("https://x.com/honchodotdev/status/123")


def test_body_markers_match_disambiguates_homonyms() -> None:
    memoryos = {
        "id": "memoryos",
        "name": "MemoryOS",
        "body_markers": ["BAI-LAB", "github.com/BAI-LAB/MemoryOS"],
    }
    assert body_markers_match("MemoryOS gamified mind palace app on Kickstarter", memoryos) is False
    assert body_markers_match(
        "MemoryOS from BAI-LAB adds long-term memory for LLM agents",
        memoryos,
    )
    assert body_markers_match("anything", {"id": "mem0", "name": "Mem0"}) is True
    memori = {
        "id": "memori",
        "name": "Memori",
        "body_markers": [
            "MemoriLabs",
            "memorilabs.ai",
            "github.com/GibsonAI/memori",
            "github.com/gibsonai",
        ],
    }
    assert body_markers_match("AI journaling app called Memori", memori) is False
    assert body_markers_match("We open sourced Memori from MemoriLabs on GitHub", memori)
    assert body_markers_match("Show HN: Memori (github.com/gibsonai)", memori)
    memu = {
        "id": "memu",
        "name": "memU",
        "body_markers": ["NevaMind-AI", "github.com/NevaMind-AI/memU", "memu.so"],
    }
    assert body_markers_match("Is MEmu Android emulator safe to use?", memu) is False
    assert body_markers_match("Built with memU from NevaMind-AI on GitHub", memu)
    everos = {
        "id": "everos",
        "name": "EverOS",
        "body_markers": ["EverMind-AI", "github.com/EverMind-AI/EverOS", "docs.evermind.ai"],
    }
    assert body_markers_match("Everos world map for my fantasy campaign", everos) is False
    assert body_markers_match("Meet EverOS from EverMind-AI on GitHub", everos)
    lightrag = {
        "id": "lightrag",
        "name": "LightRAG",
        "body_markers": ["HKUDS", "github.com/HKUDS/LightRAG", "lightrag-hku"],
    }
    assert body_markers_match("What is a light RAG approach for small docs?", lightrag) is False
    assert body_markers_match("LightRAG from HKUDS on GitHub is fast", lightrag)
    sillytavern = {
        "id": "sillytavern",
        "name": "SillyTavern",
        "body_markers": ["SillyTavern", "docs.sillytavern.app"],
    }
    assert body_markers_match("Best tavern apps for D&D roleplay", sillytavern) is False
    assert body_markers_match("SillyTavern world info keeps forgetting", sillytavern)


def test_reddit_subreddit_prefix_collision_drops_homonyms() -> None:
    zep = {"id": "zep", "name": "Zep Cloud"}
    assert product_named_in_url_or_title(
        "https://www.reddit.com/r/Zepbound/comments/abc/on_zep_cloud_9/",
        "On Zep Cloud 9",
        zep,
    ) is False
    assert product_named_in_url_or_title(
        "https://www.reddit.com/r/LocalLLaMA/comments/abc/zep_cloud_review/",
        "Zep Cloud memory review",
        zep,
    )


def test_community_confirm_drops_sibling_producthunt_pages() -> None:
    mem0 = {"id": "mem0", "name": "Mem0"}
    assert product_named_in_url_or_title(
        "https://www.producthunt.com/products/mem0-5",
        "Mem0: Persistent Memory Layer for AI Agents",
        mem0,
    )
    assert product_named_in_url_or_title(
        "https://news.ycombinator.com/item?id=41447317",
        "Show HN: Mem0 – open-source Memory Layer for AI apps",
        mem0,
    )
    assert not product_named_in_url_or_title(
        "https://www.producthunt.com/products/gstack",
        "GStack: Use Garry Tan's exact Claude Code setup",
        mem0,
    )
    assert not product_named_in_url_or_title(
        "https://www.producthunt.com/products/openmemory-chrome-extension",
        "OpenMemory Chrome Extension: Sync memory across AI's",
        mem0,
    )
    queries = community_confirm_queries("producthunt.com", mem0)
    assert any('intitle:"Mem0"' in q for q in queries)
    assert any("products/mem0" in q for q in queries)


def test_code_listed_paths_only(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Mem0\n", encoding="utf-8")
    memory = tmp_path / "mem0" / "memory"
    memory.mkdir(parents=True)
    (memory / "main.py").write_text("def add():\n    pass\n", encoding="utf-8")
    (memory / "storage.py").write_text("def save():\n    pass\n", encoding="utf-8")
    cli = tmp_path / "cli"
    cli.mkdir()
    (cli / "app.py").write_text("def add_memory():\n    pass\n", encoding="utf-8")
    picked = select_listed_code_files(
        tmp_path,
        ["README.md", "mem0/memory/main.py", "cli/missing.py"],
    )
    names = [p.relative_to(tmp_path).as_posix() for p in picked.files]
    assert names == ["README.md", "mem0/memory/main.py"]
    assert "mem0/memory/storage.py" not in names
    assert "cli/app.py" not in names
    assert any(row["path"] == "cli/missing.py" for row in picked.skipped)


def test_code_listed_paths_skip_package_stubs(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# GraphRAG\n", encoding="utf-8")
    pkg = tmp_path / "graphrag"
    pkg.mkdir()
    (pkg / "__init__.py").write_text(
        '"""The GraphRAG package."""\n',
        encoding="utf-8",
    )
    (pkg / "query.py").write_text("def search():\n    pass\n", encoding="utf-8")
    picked = select_listed_code_files(
        tmp_path,
        ["README.md", "graphrag/__init__.py", "graphrag/query.py"],
    )
    names = [p.relative_to(tmp_path).as_posix() for p in picked.files]
    assert names == ["README.md", "graphrag/query.py"]
    assert any(
        row["path"] == "graphrag/__init__.py" and row["reason"] == "stub"
        for row in picked.skipped
    )


def test_code_listed_paths_skip_empty_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Mem0\n", encoding="utf-8")
    memory = tmp_path / "mem0" / "memory"
    memory.mkdir(parents=True)
    (memory / "main.py").write_text("def add():\n    pass\n", encoding="utf-8")
    (memory / "__init__.py").write_bytes(b"")
    picked = select_listed_code_files(
        tmp_path,
        ["README.md", "mem0/memory/main.py", "mem0/memory/__init__.py"],
    )
    names = [p.relative_to(tmp_path).as_posix() for p in picked.files]
    assert names == ["README.md", "mem0/memory/main.py"]
    assert any(
        row["path"] == "mem0/memory/__init__.py" and row["reason"] == "empty"
        for row in picked.skipped
    )


def test_code_steals_infra_slots_for_high_packages(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Honcho\n", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "models.py").write_text("class Peer:\n    pass\n", encoding="utf-8")
    deriver = src / "deriver"
    deriver.mkdir()
    (deriver / "deriver.py").write_text("class Deriver:\n    pass\n", encoding="utf-8")
    (deriver / "consumer.py").write_text("def search_memory():\n    pass\n", encoding="utf-8")
    (deriver / "enqueue.py").write_text("def search_memory():\n    pass\n", encoding="utf-8")
    llm = src / "llm"
    llm.mkdir()
    for i in range(6):
        (llm / f"backend_{i}.py").write_text("def embed():\n    pass\n", encoding="utf-8")
    for i in range(20):
        pack = src / f"pack_{i:02d}"
        pack.mkdir()
        (pack / "mod.py").write_text("def search_memory():\n    pass\n", encoding="utf-8")
    product = {"id": "honcho", "name": "Honcho"}
    names = [
        p.relative_to(tmp_path).as_posix()
        for p in select_code_files(tmp_path, product)
    ]
    deriver_kept = [name for name in names if name.startswith("src/deriver/")]
    assert len(deriver_kept) >= 3
    assert "src/deriver/deriver.py" in deriver_kept
    assert "src/deriver/consumer.py" in deriver_kept


def test_code_skips_tests_directory_and_test_prefix(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Honcho\n", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "memory.py").write_text("def search_memory():\n    pass\n", encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "memory.py").write_text("def search_memory():\n    pass\n", encoding="utf-8")
    (src / "test_store.py").write_text("def search_memory():\n    pass\n", encoding="utf-8")
    names = [
        p.relative_to(tmp_path).as_posix()
        for p in select_code_files(tmp_path, {"id": "honcho", "name": "Honcho"})
    ]
    assert "src/memory.py" in names
    assert all("tests/" not in name for name in names)
    assert "src/test_store.py" not in names


def test_code_skips_integrations_and_js_tests(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Mem0\n", encoding="utf-8")
    memory = tmp_path / "mem0" / "memory"
    memory.mkdir(parents=True)
    (memory / "main.py").write_text("def add_memory():\n    pass\n", encoding="utf-8")
    plugin = tmp_path / "integrations" / "cursor-plugin" / "core"
    plugin.mkdir(parents=True)
    (plugin / "memory_core.py").write_text("def add_memory():\n    pass\n", encoding="utf-8")
    n8n_test = tmp_path / "integrations" / "n8n" / "test"
    n8n_test.mkdir(parents=True)
    (n8n_test / "Mem0.node.test.ts").write_text("search_memory()\n", encoding="utf-8")
    (tmp_path / "mem0" / "scoping.test.ts").write_text(
        "function search_memory() {}\n", encoding="utf-8"
    )
    names = [
        p.relative_to(tmp_path).as_posix()
        for p in select_code_files(tmp_path, {"id": "mem0", "name": "Mem0"})
    ]
    assert "mem0/memory/main.py" in names
    assert all("integrations/" not in name for name in names)
    assert "mem0/scoping.test.ts" not in names


def test_code_prefers_package_memory_over_cli(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Mem0\n", encoding="utf-8")
    memory = tmp_path / "mem0" / "memory"
    memory.mkdir(parents=True)
    for name in ("base.py", "main.py", "storage.py", "utils.py"):
        (memory / name).write_text("def add_memory():\n    pass\n", encoding="utf-8")
    cli = tmp_path / "cli" / "python" / "src"
    cli.mkdir(parents=True)
    (cli / "app.py").write_text("def add_memory():\n    pass\n", encoding="utf-8")
    ts_llm = tmp_path / "mem0-ts" / "src" / "oss" / "src" / "llms"
    ts_llm.mkdir(parents=True)
    (ts_llm / "langchain.ts").write_text("function add_memory() {}\n", encoding="utf-8")
    names = [
        p.relative_to(tmp_path).as_posix()
        for p in select_code_files(tmp_path, {"id": "mem0", "name": "Mem0"})
    ]
    memory_kept = [name for name in names if name.startswith("mem0/memory/")]
    assert len(memory_kept) >= 3
    assert "mem0/memory/storage.py" in memory_kept


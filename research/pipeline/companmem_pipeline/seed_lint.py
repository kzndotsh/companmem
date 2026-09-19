"""Lint seed.json structure and optional live URL reachability."""

from __future__ import annotations

import argparse
from urllib.parse import urlparse

import httpx

from pathlib import Path

from companmem_pipeline.harvest import load_seed, select_listed_code_files
from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.paths import CACHE_DIR, EVAL_CACHE_DIR, SEED_PATH

REQUIRED_KEYS = (
    "id",
    "name",
    "repo",
    "docs",
    "clone",
    "community",
    "skip_url_prefixes",
    "open_code",
    "open_docs",
)

BOT_BLOCKED_DOC_HOSTS = frozenset({"help.replika.com"})

ZEP_GRAPHITI_SKIP = (
    "https://github.com/getzep/graphiti",
    "https://help.getzep.com/graphiti",
)


class SeedLintError(Exception):
    """seed.json failed lint."""


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _lint_seed_entries(
    entries: dict[str, object],
    *,
    section: str,
) -> list[str]:
    errors: list[str] = []
    for slug, entry in entries.items():
        if not isinstance(entry, dict):
            errors.append(f"{slug}: {section} entry is not an object")
            continue
        prefix = f"{slug}:"
        for key in REQUIRED_KEYS:
            if key not in entry:
                errors.append(f"{prefix} missing {key}")
        entry_id = str(entry.get("id") or "")
        if entry_id != slug:
            errors.append(f"{prefix} id '{entry_id}' does not match key '{slug}'")
        docs = entry.get("docs")
        if isinstance(docs, str) and docs and not _is_url(docs):
            errors.append(f"{prefix} docs is not a valid URL")
        repo = entry.get("repo")
        if repo is not None and repo != "" and not _is_url(str(repo)):
            errors.append(f"{prefix} repo is not a valid URL")
        clone = entry.get("clone")
        open_code = entry.get("open_code")
        if not isinstance(open_code, list):
            errors.append(f"{prefix} open_code must be a list")
        elif clone is True and not open_code:
            errors.append(f"{prefix} clone=true but open_code is empty")
        if clone is False:
            if repo:
                errors.append(f"{prefix} clone=false but repo is set")
            if isinstance(open_code, list) and open_code:
                errors.append(f"{prefix} clone=false but open_code is non-empty")
        open_docs = entry.get("open_docs")
        if not isinstance(open_docs, list):
            errors.append(f"{prefix} open_docs must be a list")
        elif not open_docs:
            errors.append(f"{prefix} open_docs is empty")
        else:
            for url in open_docs:
                if not isinstance(url, str) or not _is_url(url):
                    errors.append(f"{prefix} open_docs has invalid URL: {url!r}")
        if section == "products" and slug == "zep":
            skips = [str(p) for p in (entry.get("skip_url_prefixes") or [])]
            for required in ZEP_GRAPHITI_SKIP:
                if required not in skips:
                    errors.append(f"{prefix} skip_url_prefixes missing {required}")
            for url in open_docs or []:
                if isinstance(url, str) and "/graphiti" in url:
                    errors.append(f"{prefix} open_docs must not include /graphiti ({url})")
        if section == "products" and slug == "graphiti":
            for url in open_docs or []:
                if not isinstance(url, str):
                    continue
                host = urlparse(url).netloc
                if host == "help.getzep.com" and "/graphiti" not in url:
                    errors.append(
                        f"{prefix} graphiti open_docs on help.getzep.com must stay under /graphiti ({url})"
                    )
    return errors


def lint_seed_structure(seed: dict[str, object]) -> list[str]:
    errors: list[str] = []
    products = seed.get("products")
    if not isinstance(products, dict) or not products:
        errors.append("products: missing or empty")
        return errors

    evals = seed.get("evals")
    if evals is None:
        errors.append("evals: missing (use empty object if none)")
    elif not isinstance(evals, dict):
        errors.append("evals: must be an object")
        evals = {}

    errors.extend(_lint_seed_entries(products, section="products"))
    if isinstance(evals, dict):
        errors.extend(_lint_seed_entries(evals, section="evals"))
        product_keys = set(products.keys())
        eval_keys = set(evals.keys())
        for slug in sorted(product_keys & eval_keys):
            errors.append(f"{slug}: id appears in both products and evals")
    return errors


def _cloudflare_bot_block(response: httpx.Response) -> bool:
    if response.status_code != 403:
        return False
    return (response.headers.get("cf-mitigated") or "").lower() == "challenge"


def _lint_seed_urls_for_entries(
    entries: dict[str, object],
    *,
    client: httpx.Client,
) -> list[str]:
    errors: list[str] = []
    for slug, product in entries.items():
        if not isinstance(product, dict):
            continue
        prefix = f"{slug}:"
        docs = str(product.get("docs") or "").strip()
        if docs:
            try:
                response = client.get(docs)
            except httpx.HTTPError as exc:
                errors.append(f"{prefix} docs fetch failed ({docs}): {exc}")
            else:
                host = urlparse(docs).netloc.lower()
                if response.status_code >= 400:
                    if host in BOT_BLOCKED_DOC_HOSTS and _cloudflare_bot_block(response):
                        pass
                    else:
                        errors.append(
                            f"{prefix} docs HTTP {response.status_code} ({docs})"
                        )
                elif len(response.content) < 50:
                    errors.append(f"{prefix} docs body too small ({docs})")
        repo = product.get("repo")
        if isinstance(repo, str) and repo:
            try:
                response = client.head(repo)
            except httpx.HTTPError as exc:
                errors.append(f"{prefix} repo HEAD failed ({repo}): {exc}")
            else:
                if response.status_code >= 400:
                    errors.append(f"{prefix} repo HTTP {response.status_code} ({repo})")
        for url in product.get("open_docs") or []:
            if not isinstance(url, str) or not url:
                continue
            try:
                response = client.get(url)
            except httpx.HTTPError as exc:
                errors.append(f"{prefix} open_docs fetch failed ({url}): {exc}")
                continue
            if response.status_code >= 400:
                errors.append(f"{prefix} open_docs HTTP {response.status_code} ({url})")
            elif len(response.content) < 100:
                errors.append(f"{prefix} open_docs body too small ({url})")
    return errors


def lint_seed_urls(seed: dict[str, object], *, client: httpx.Client) -> list[str]:
    errors: list[str] = []
    products = seed.get("products")
    if not isinstance(products, dict):
        return ["products: missing"]
    errors.extend(_lint_seed_urls_for_entries(products, client=client))
    evals = seed.get("evals")
    if isinstance(evals, dict) and evals:
        errors.extend(_lint_seed_urls_for_entries(evals, client=client))
    return errors


def lint_open_code_paths(
    seed: dict[str, object],
    *,
    cache_dir: Path = CACHE_DIR,
    require_clones: bool = False,
) -> list[str]:
    """Verify seed open_code paths exist in harvested repo clones."""
    errors: list[str] = []

    def check_section(entries: dict[str, object], section_cache: Path) -> None:
        for slug, product in entries.items():
            if not isinstance(product, dict) or not product.get("clone"):
                continue
            prefix = f"{slug}:"
            listed = product.get("open_code")
            if not isinstance(listed, list):
                continue
            repo_dir = section_cache / slug / "repo"
            if not (repo_dir / ".git").exists():
                if require_clones:
                    errors.append(f"{prefix} open_code not checked (no clone at {repo_dir})")
                continue
            selection = select_listed_code_files(repo_dir, listed)
            for skipped in selection.skipped:
                reason = skipped.get("reason")
                path = skipped.get("path")
                if reason == "missing":
                    errors.append(f"{prefix} open_code missing in repo: {path}")
                elif reason == "empty":
                    errors.append(f"{prefix} open_code empty in repo: {path}")
                elif reason == "stub":
                    errors.append(f"{prefix} open_code package stub in repo: {path}")
                elif reason == "outside_repo":
                    errors.append(f"{prefix} open_code outside repo: {path}")

    products = seed.get("products")
    if not isinstance(products, dict):
        return ["products: missing"]
    check_section(products, cache_dir)
    return errors


def lint_seed(
    *,
    check_urls: bool = False,
    check_open_code: bool = False,
    require_clones: bool = False,
    namespace: str = "all",
) -> list[str]:
    seed = load_seed()
    errors = lint_seed_structure(seed)
    if check_open_code and not errors:
        if namespace in ("product", "all"):
            errors.extend(
                lint_open_code_paths(seed, cache_dir=CACHE_DIR, require_clones=require_clones),
            )
        if namespace in ("eval", "all"):
            evals = seed.get("evals")
            if isinstance(evals, dict) and evals:
                errors.extend(
                    lint_open_code_paths(
                        {"products": evals},
                        cache_dir=EVAL_CACHE_DIR,
                        require_clones=require_clones,
                    ),
                )
    if check_urls and not errors:
        headers = {
            "User-Agent": "CompanmemResearch/0.1",
            "Accept": "text/markdown, text/html, application/json, */*",
        }
        with httpx.Client(follow_redirects=True, timeout=30, headers=headers) as client:
            errors.extend(lint_seed_urls(seed, client=client))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint research/pipeline/seed.json")
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="GET docs/open_docs and HEAD repo for every product",
    )
    parser.add_argument(
        "--check-open-code",
        action="store_true",
        help="Verify open_code paths against cached repo clones when present",
    )
    parser.add_argument(
        "--namespace",
        choices=("product", "eval", "all"),
        default="all",
        help="Which seed section to check open_code against (default all)",
    )
    parser.add_argument(
        "--require-clones",
        action="store_true",
        help="With --check-open-code, fail if any clone=true product has no cached repo",
    )
    args = parser.parse_args()
    with PipelineLogger("seed_lint", source="seed") as log:
        errors = lint_seed(
            check_urls=args.check_urls,
            check_open_code=args.check_open_code,
            require_clones=args.require_clones,
            namespace=args.namespace,
        )
        if errors:
            log.error("seed_lint_fail", path=str(SEED_PATH), errors=errors[:30])
            print(f"FAIL {SEED_PATH}")
            for err in errors:
                print(f"  {err}")
            raise SystemExit(1)
        log.info(
            "seed_lint_ok",
            path=str(SEED_PATH),
            check_urls=args.check_urls,
            check_open_code=args.check_open_code,
            require_clones=args.require_clones,
        )
        print(f"ok {SEED_PATH}")


if __name__ == "__main__":
    main()

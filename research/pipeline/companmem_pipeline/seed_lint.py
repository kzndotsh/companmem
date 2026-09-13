"""Lint seed.json structure and optional live URL reachability."""

from __future__ import annotations

import argparse
from urllib.parse import urlparse

import httpx

from companmem_pipeline.harvest import load_seed
from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.paths import SEED_PATH

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


def lint_seed_structure(seed: dict[str, object]) -> list[str]:
    errors: list[str] = []
    products = seed.get("products")
    if not isinstance(products, dict) or not products:
        errors.append("products: missing or empty")
        return errors

    for slug, product in products.items():
        if not isinstance(product, dict):
            errors.append(f"{slug}: product entry is not an object")
            continue
        prefix = f"{slug}:"
        for key in REQUIRED_KEYS:
            if key not in product:
                errors.append(f"{prefix} missing {key}")
        product_id = str(product.get("id") or "")
        if product_id != slug:
            errors.append(f"{prefix} id '{product_id}' does not match key '{slug}'")
        docs = product.get("docs")
        if isinstance(docs, str) and docs and not _is_url(docs):
            errors.append(f"{prefix} docs is not a valid URL")
        repo = product.get("repo")
        if repo is not None and repo != "" and not _is_url(str(repo)):
            errors.append(f"{prefix} repo is not a valid URL")
        clone = product.get("clone")
        if clone is False:
            if repo:
                errors.append(f"{prefix} clone=false but repo is set")
            open_code = product.get("open_code")
            if isinstance(open_code, list) and open_code:
                errors.append(f"{prefix} clone=false but open_code is non-empty")
        open_docs = product.get("open_docs")
        if not isinstance(open_docs, list):
            errors.append(f"{prefix} open_docs must be a list")
        elif not open_docs:
            errors.append(f"{prefix} open_docs is empty")
        else:
            for url in open_docs:
                if not isinstance(url, str) or not _is_url(url):
                    errors.append(f"{prefix} open_docs has invalid URL: {url!r}")
        if slug == "zep":
            skips = [str(p) for p in (product.get("skip_url_prefixes") or [])]
            for required in ZEP_GRAPHITI_SKIP:
                if required not in skips:
                    errors.append(f"{prefix} skip_url_prefixes missing {required}")
            for url in open_docs or []:
                if isinstance(url, str) and "/graphiti" in url:
                    errors.append(f"{prefix} open_docs must not include /graphiti ({url})")
        if slug == "graphiti":
            for url in open_docs or []:
                if not isinstance(url, str):
                    continue
                host = urlparse(url).netloc
                if host == "help.getzep.com" and "/graphiti" not in url:
                    errors.append(
                        f"{prefix} graphiti open_docs on help.getzep.com must stay under /graphiti ({url})"
                    )
    return errors


def _cloudflare_bot_block(response: httpx.Response) -> bool:
    if response.status_code != 403:
        return False
    return (response.headers.get("cf-mitigated") or "").lower() == "challenge"


def lint_seed_urls(seed: dict[str, object], *, client: httpx.Client) -> list[str]:
    errors: list[str] = []
    products = seed.get("products")
    if not isinstance(products, dict):
        return ["products: missing"]

    for slug, product in products.items():
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


def lint_seed(*, check_urls: bool = False) -> list[str]:
    seed = load_seed()
    errors = lint_seed_structure(seed)
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
    args = parser.parse_args()
    with PipelineLogger("seed_lint", source="seed") as log:
        errors = lint_seed(check_urls=args.check_urls)
        if errors:
            log.error("seed_lint_fail", path=str(SEED_PATH), errors=errors[:30])
            print(f"FAIL {SEED_PATH}")
            for err in errors:
                print(f"  {err}")
            raise SystemExit(1)
        log.info("seed_lint_ok", path=str(SEED_PATH), check_urls=args.check_urls)
        print(f"ok {SEED_PATH}")


if __name__ == "__main__":
    main()

# google_claim_search.py
import json
import re
from typing import Optional, List, Dict, Any
from io import BytesIO
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from pydantic import BaseModel, Field
import requests
from rank_bm25 import BM25Okapi
import cloudscraper
import logging

TOP_K_RESULTS = 5         # how many search results to fetch (for fallback)
MAX_SUCCESSFUL_PAGES = 1  # how many successfully fetched pages to return
_PAT = re.compile(r"(content|main|article|body|post)", re.I)
_SPLIT_RE = re.compile(r"\n{2,}")          # paragraph boundary = ≥2 new-lines
_TOKEN_RE = re.compile(r"\w+")

def _candidate_blocks(soup: BeautifulSoup) -> List[BeautifulSoup]:
    """Return potential ‘main content’ elements in priority order."""
    # ① semantic tags
    blocks = soup.find_all(["main", "article"])
    if blocks:
        return blocks

    # ② id/class pattern match (limit scan to first ~40 nodes for speed)
    for tag in soup.find_all(["div", "section"], limit=40):
        ident = " ".join(tag.get("class", [])) + " " + (tag.get("id") or "")
        if _PAT.search(ident):
            blocks.append(tag)
    return blocks


def _biggest_text_container(soup: BeautifulSoup) -> Optional[BeautifulSoup]:
    """
    Pick the best container for the article body.
    """
    total_len = len(soup.get_text(" ", strip=True))
    best, best_len = None, 0

    for cand in _candidate_blocks(soup):
        txt_len = len(cand.get_text(" ", strip=True))
        if txt_len > best_len:
            best, best_len = cand, txt_len

    # Fallback: largest <div>/<section> if patterns failed
    if not best:
        for cand in soup.find_all(["div", "section"], limit=30):
            txt_len = len(cand.get_text(" ", strip=True))
            if txt_len > best_len:
                best, best_len = cand, txt_len

    # sanity: only accept if it’s at least 25 % of whole-page text
    if best and best_len > 0.25 * total_len:
        return best
    return None


def _clean_html(html: str) -> str:
    """
    Extract the main article text as **Markdown** with *no* heavy dependencies.
    """
    soup = BeautifulSoup(html, "html.parser")

    # 🔹 1. Drop obvious non-content nodes
    for tag in soup(["script", "style", "noscript", "header",
                     "footer", "nav", "aside", "iframe"]):
        tag.decompose()

    # 🔹 2. Choose the core container
    container = _biggest_text_container(soup) or soup.body or soup

    # 🔹 3. Convert to Markdown
    markdown = md(
        str(container),
        strip=["img", "iframe", "script", "style"],
        heading_style="ATX",
        bullets="*",
    )

    # 🔹 4. Whitespace tidy-up
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    markdown = re.sub(r"[ \t]{2,}", " ", markdown).strip()

    return markdown or "[content-extraction-failed]"


def _split_passages(text: str,
                    max_chars: int = 3000,
                    min_chars: int = 600) -> List[str]:
    """
    Split Markdown into ~paragraph-sized passages.

    1. First split on double-newline (natural paras).
    2. Merge consecutive short paras until >= min_chars.
    3. Hard-split any monster chunk longer than max_chars.
    """
    #print("text: ", text)
    
    parts, current, passages = _SPLIT_RE.split(text), [], []
    def flush():
        if current:
            chunk = "\n\n".join(current).strip()
            while len(chunk) > max_chars:   # hard split long tail
                passages.append(chunk[:max_chars])
                chunk = chunk[max_chars:]
            if chunk:
                passages.append(chunk)
            current.clear()

    for para in parts:
        if len(" ".join(current) + para) < min_chars:
            current.append(para)
        else:
            current.append(para)
            flush()
    flush()
    #print("passage: ", passages)
    #print()
    return passages

def _tokenize(txt: str) -> List[str]:
    return _TOKEN_RE.findall(txt.lower())


def _top_passages(claim: str,
                  passages: List[str],
                  k: int = 3) -> List[str]:
    if not passages:
        return []
    
    tokenized = [_tokenize(p) for p in passages]
    if all(len(toks) == 0 for toks in tokenized):
        return passages[:k]  # fallback

    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(_tokenize(claim))
    ranked = sorted(zip(scores, passages), reverse=True)[:k]
    # keep only passages with non-zero score; fall back to first k otherwise
    picked = [p for s, p in ranked if s > 0] or passages[:k]
    #print('picked : ', picked)
    return picked

class GoogleClaimSearch(BaseModel):
    """
    LiteLLM-compatible tool:
    given a claim, return plain-text evidence passages from Google
    """
    api_key: str = Field(..., description="Google Custom Search API key")
    cx: str = Field(..., description="Google Programmable Search Engine ID")
    tool_call_counts: int = 0

    class Config:
        arbitrary_types_allowed = True

    def _fetch(self, url: str) -> Dict[str, Any]:
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    "browser": "chrome",
                    "platform": "windows",
                    "mobile": False
                }
            )
            page = scraper.get(url, headers={"User-Agent": "Mozilla/5.0"})
            page.raise_for_status()
            
            # Check if the content is a PDF
            content_type = page.headers.get('Content-Type', '').lower()
            is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')
            
            if is_pdf:
                # Extract text from PDF
                try:
                    import pdfplumber; _pdf = pdfplumber.open(BytesIO(page.content))
                    with _pdf as pdf:
                        full_text = ""
                        for page_obj in pdf.pages:
                            text = page_obj.extract_text()
                            if text:
                                full_text += text + "\n"
                        
                        # Use filename or URL as title for PDFs
                        title = url.split('/')[-1] if '/' in url else "PDF Document"
                        cleaned = full_text.strip()
                        return {"title": title, "cleaned": cleaned}
                except Exception as pdf_error:
                    return {"title": "", "error": f"[Error extracting PDF] {pdf_error}"}
            else:
                # Handle HTML content
                soup = BeautifulSoup(page.text, "html.parser")
                title = (soup.title.string or "").strip() if soup.title else ""
                cleaned = _clean_html(page.text)
                return {"title": title, "cleaned": cleaned}
        except Exception as e:
            return {"title": "", "error": f"[Error fetching] {e}"}
    
    # ------------- tool entry point -------------
    def invoke_single(self, claim: str, q: str, gl: str) -> str:
        """
        Parameters
        ----------
        claim : str
            A factual claim / statement in natural language.
        
        q: str
            A keyword that needs to be searched for fact verification.
            This is usually a word/phrase within the claim.

        Returns
        -------
        str
            JSON stringified list[str] – each element is the cleaned text
            of a search-result page.  Errors become single-element lists.
        """
        try:
            search_url = "https://www.googleapis.com/customsearch/v1"
            q_params = {
                "q": q,
                "key": self.api_key,
                "cx": self.cx,
                "num": TOP_K_RESULTS, # top 5 results
                "gl": gl,             # geolocation
            }
            resp = requests.get(search_url, params=q_params, timeout=6)
            resp.raise_for_status()
            self.tool_call_counts += 1
            items = resp.json().get("items", [])

            results: List[Dict[str, Any]] = []
            failed_attempts: List[Dict[str, str]] = []  # Track failed URLs for debugging
            successful_count = 0
            
            for it in items:
                # Stop if we have enough successful results
                if successful_count >= MAX_SUCCESSFUL_PAGES:
                    break
                    
                url = it.get("link")
                if not url:
                    continue

                fetched = self._fetch(url)
                if "error" in fetched:
                    # Don't return error immediately, track it and try next URL
                    failed_attempts.append({"url": url, "error": fetched["error"]})
                    continue
                    
                # Treat '[content-extraction-failed]' as a failure
                if fetched["cleaned"].strip() == "[content-extraction-failed]":
                    failed_attempts.append({"url": url, "error": "[content-extraction-failed]"})
                    continue

                passages = _split_passages(fetched["cleaned"])
                if not passages or all(not p.strip() for p in passages):
                    # No meaningful content extracted, try next URL
                    failed_attempts.append({"url": url, "error": "No meaningful content extracted"})
                    continue

                top_passages = _top_passages(claim, passages)
                if not top_passages or all(not p.strip() for p in top_passages):
                    # No relevant passages found, try next URL
                    failed_attempts.append({"url": url, "error": "No relevant passages found"})
                    continue

                results.append({
                    'query': q,
                    "title": fetched["title"],
                    "link": url,
                    "gl": gl,
                    "text_block": top_passages
                })
                successful_count += 1
                
            # Only return error if ALL URLs failed
            if not results:
                error_details = "; ".join([f"{fa['url']}: {fa['error']}" for fa in failed_attempts[:3]])
                results = [{
                    "query": q,
                    "title": "",
                    "link": "",
                    "gl": gl,
                    "text_block": [f"Failed to extract text from all {len(failed_attempts)} URLs tried. Details: {error_details}"]
                }]
            return json.dumps(results, ensure_ascii=False)

        except Exception as outer:
            error_msg = str(outer)
            if "400 Client Error" in error_msg:
                raise RuntimeError(f"Google API 400 Bad Request error - terminating interview: {outer}") from outer
            return json.dumps([{"query" : q, "title": "", "link":"", "gl" : gl, "text_block":f"Search failure: {outer}"}], ensure_ascii=False)

    # ------------- schema that LiteLLM exports -------------
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "google_claim_search",
                "description": (
                    "Given a factual `claim`, run Google Custom Search with the query (keyword) `q`, and `gl`."
                    f"crawl search result pages (trying up to {TOP_K_RESULTS} URLs with fallback on failure), "
                    "and return extracted plain texts as a JSON string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "q": {
                            "type": "string",
                            "description": "Query; a keyword that needs to be searched for fact verification. Do not include quotation marks.",
                        },
                        "gl": {
                            "type": "string",
                            "description": "Geolocation of end user. The country code (e.g., 'us', 'uk', 'ca', 'jp', 'kr') to tailor search results to a specific region.",
                        },
                    },
                    "required": ["q", "gl"],
                },
            },
        }
        
    def invoke(self, claims: List[str], q: str, gl: str) -> str:
        """
        Process multiple claims with the same query and geolocation.
        
        Parameters
        ----------
        claims : List[str]
            A list of factual claims / statements in natural language.
        
        q: str
            A keyword that needs to be searched for fact verification.

        gl: str
            Geolocation country code.

        Returns
        -------
        str
            JSON stringified dict mapping each claim to its relevant passages.
        """
        try:
            search_url = "https://www.googleapis.com/customsearch/v1"
            q_params = {
                "q": q,
                "key": self.api_key,
                "cx": self.cx,
                "num": TOP_K_RESULTS,
                "gl": gl,
            }
            resp = requests.get(search_url, params=q_params, timeout=6)
            resp.raise_for_status()
            self.tool_call_counts += 1
            items = resp.json().get("items", [])

            # Fetch pages with fallback - try URLs until we get content
            all_passages: List[str] = []
            page_info: List[Dict[str, Any]] = []
            failed_attempts: List[Dict[str, str]] = []
            successful_count = 0
            
            for it in items:
                # Stop if we have enough successful results
                if successful_count >= MAX_SUCCESSFUL_PAGES:
                    break
                    
                url = it.get("link")
                if not url:
                    continue

                fetched = self._fetch(url)
                if "error" in fetched:
                    # Track failure and try next URL
                    failed_attempts.append({"url": url, "error": fetched["error"]})
                    continue
                    
                # Treat '[content-extraction-failed]' as a failure
                if fetched["cleaned"].strip() == "[content-extraction-failed]":
                    failed_attempts.append({"url": url, "error": "[content-extraction-failed]"})
                    continue

                passages = _split_passages(fetched["cleaned"])
                if not passages or all(not p.strip() for p in passages):
                    # No meaningful content, try next URL
                    failed_attempts.append({"url": url, "error": "No meaningful content extracted"})
                    continue

                all_passages.extend(passages)
                page_info.append({"title": fetched["title"], "link": url})
                successful_count += 1

            # For each claim, find the most relevant passages
            passages_set = []
            if not all_passages:
                error_details = "; ".join([f"{fa['url']}: {fa['error']}" for fa in failed_attempts[:3]])
                results = [{
                        "query": q,
                        "gl": gl,
                        "pages": page_info,
                        "failed_attempts": len(failed_attempts),
                        "text_block": [f"Failed to extract text from all {len(failed_attempts)} URLs tried. Details: {error_details}"]
                    }]
            else:
                for claim in claims:
                    top_passages = _top_passages(claim, all_passages)
                    passages_set.extend(top_passages)
                    passages_set = list(set(passages_set))  # remove duplicates
                results =[{
                    "query": q,
                    "gl": gl,
                    "pages": page_info,
                    "text_block": passages_set
                }]        
                   

            return json.dumps(results, ensure_ascii=False)
        except Exception as outer:
            error_msg = str(outer)
            if "400 Client Error" in error_msg:
                raise RuntimeError(f"Google API 400 Bad Request error - terminating interview: {outer}") from outer
            error_result = [{"query": q, "gl": gl, "text_block": f"Search failure: {outer}"}]
            return json.dumps(error_result, ensure_ascii=False)

    def calculate_cost(self) -> float:
        # Custom Search API costs
        # 100 queries per day are free
        # $5 per 1000 queries thereafter
        free_quota = 2500
        cost_per_1000 = 5.0
        billable_calls = max(0, self.tool_call_counts - free_quota)
        total_cost = (billable_calls / 1000) * cost_per_1000
        return total_cost


class SerperSearch(BaseModel):
    """
    LiteLLM-compatible tool:
    given a claim, return plain-text evidence passages using Serper (Google Search API alternative).
    Serper returns search result URLs; pages are crawled the same way as GoogleClaimSearch.
    """
    api_key: str = Field(..., description="Serper API key")
    tool_call_counts: int = 0

    class Config:
        arbitrary_types_allowed = True

    def _fetch(self, url: str) -> Dict[str, Any]:
        try:
            scraper = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "mobile": False}
            )
            page = scraper.get(url, headers={"User-Agent": "Mozilla/5.0"})
            page.raise_for_status()

            content_type = page.headers.get('Content-Type', '').lower()
            is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')

            if is_pdf:
                try:
                    import pdfplumber; _pdf = pdfplumber.open(BytesIO(page.content))
                    with _pdf as pdf:
                        full_text = "".join(
                            (p.extract_text() or "") + "\n" for p in pdf.pages
                        )
                    title = url.split('/')[-1] if '/' in url else "PDF Document"
                    return {"title": title, "cleaned": full_text.strip()}
                except Exception as pdf_error:
                    return {"title": "", "error": f"[Error extracting PDF] {pdf_error}"}
            else:
                soup = BeautifulSoup(page.text, "html.parser")
                title = (soup.title.string or "").strip() if soup.title else ""
                cleaned = _clean_html(page.text)
                return {"title": title, "cleaned": cleaned}
        except Exception as e:
            return {"title": "", "error": f"[Error fetching] {e}"}

    def invoke(self, claims: List[str], q: str, gl: str, **kwargs) -> str:
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json={"q": q, "gl": gl, "num": TOP_K_RESULTS},
                timeout=10,
            )
            resp.raise_for_status()
            self.tool_call_counts += 1
            items = resp.json().get("organic", [])

            all_passages: List[str] = []
            api_snippets: List[str] = []  # always collected from Serper, regardless of crawl outcome
            page_info: List[Dict[str, Any]] = []
            failed_attempts: List[Dict[str, str]] = []
            successful_count = 0

            for it in items:
                url = it.get("link")
                snippet = it.get("snippet", "")
                title = it.get("title", "")

                # Always store the API snippet — used as guaranteed fallback evidence
                if snippet:
                    api_snippets.append(snippet)

                if not url or successful_count >= MAX_SUCCESSFUL_PAGES:
                    continue

                # Try full page crawl
                fetched = self._fetch(url)
                crawl_ok = (
                    "error" not in fetched
                    and fetched.get("cleaned", "").strip() != "[content-extraction-failed]"
                )
                if crawl_ok:
                    passages = _split_passages(fetched["cleaned"])
                    if passages and any(p.strip() for p in passages):
                        all_passages.extend(passages)
                        page_info.append({"title": fetched["title"] or title, "link": url, "source": "crawled"})
                        successful_count += 1
                        continue

                # Crawl failed — note it; snippet already saved above
                failed_attempts.append({"url": url, "error": fetched.get("error", "No meaningful content extracted")})
                if snippet:
                    page_info.append({"title": title, "link": url, "source": "api_snippet"})

            # Build text_block: prefer crawled passages; fall back to API snippets
            if all_passages:
                passages_set: List[str] = []
                for claim in claims:
                    passages_set.extend(_top_passages(claim, all_passages))
                text_block = list(set(passages_set))
            elif api_snippets:
                logging.info("[SerperSearch] All crawls failed; using API snippets as text_block.")
                text_block = ["Failed to extract text from the url. Please refer to the snippets instead."]*len(api_snippets)
            else:
                error_details = "; ".join(f"{fa['url']}: {fa['error']}" for fa in failed_attempts[:3])
                text_block = [f"Failed to extract text from all {len(failed_attempts)} URLs tried. Details: {error_details}"]

            results = [{
                "query": q,
                "gl": gl,
                "pages": page_info,
                "text_block": text_block,
                "api_snippets": api_snippets,  # always present for evaluator fallback
            }]
            return json.dumps(results, ensure_ascii=False)
        except Exception as outer:
            error_msg = str(outer)
            if "400 Client Error" in error_msg:
                raise RuntimeError(f"Serper API 400 Bad Request error - terminating interview: {outer}") from outer
            return json.dumps([{"query": q, "gl": gl, "text_block": f"Search failure: {outer}", "api_snippets": []}], ensure_ascii=False)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "serper_search",
                "description": (
                    "Given a factual claim, run a Serper (Google Search) with query `q` and geolocation `gl`, "
                    f"crawl result pages (trying up to {TOP_K_RESULTS} URLs with fallback on failure), "
                    "and return extracted plain texts as a JSON string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "q": {
                            "type": "string",
                            "description": "Search query for fact verification. Do not include quotation marks.",
                        },
                        "gl": {
                            "type": "string",
                            "description": "Geolocation country code (e.g., 'us', 'uk', 'kr') of end user to tailor search results.",
                        },
                    },
                    "required": ["q", "gl"],
                },
            },
        }

    def calculate_cost(self) -> float:
        # Serper pricing: $50 per 2500 queries (~$0.02/query) after free tier
        free_quota = 2500
        cost_per_1000 = 1.0
        billable_calls = max(0, self.tool_call_counts - free_quota)
        total_cost = (billable_calls / 1000) * cost_per_1000
        return total_cost
        #return self.tool_call_counts * cost_per_query


class TavilySearch(BaseModel):
    """
    LiteLLM-compatible tool:
    given a claim, return plain-text evidence passages using Tavily Search API.
    Tries full page crawling first; Tavily's pre-extracted content is stored as api_snippets
    and used as text_block fallback when crawling fails.
    """
    api_key: str = Field(..., description="Tavily API key")
    tool_call_counts: int = 0

    class Config:
        arbitrary_types_allowed = True

    def _fetch(self, url: str) -> Dict[str, Any]:
        try:
            scraper = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "mobile": False}
            )
            page = scraper.get(url, headers={"User-Agent": "Mozilla/5.0"})
            page.raise_for_status()

            content_type = page.headers.get('Content-Type', '').lower()
            is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')

            if is_pdf:
                try:
                    import pdfplumber; _pdf = pdfplumber.open(BytesIO(page.content))
                    with _pdf as pdf:
                        full_text = "".join(
                            (p.extract_text() or "") + "\n" for p in pdf.pages
                        )
                    title = url.split('/')[-1] if '/' in url else "PDF Document"
                    return {"title": title, "cleaned": full_text.strip()}
                except Exception as pdf_error:
                    return {"title": "", "error": f"[Error extracting PDF] {pdf_error}"}
            else:
                soup = BeautifulSoup(page.text, "html.parser")
                title = (soup.title.string or "").strip() if soup.title else ""
                cleaned = _clean_html(page.text)
                return {"title": title, "cleaned": cleaned}
        except Exception as e:
            return {"title": "", "error": f"[Error fetching] {e}"}

    def invoke(self, claims: List[str], q: str, gl: str, **kwargs) -> str:
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.api_key,
                    "query": q,
                    "search_depth": "basic",
                    "max_results": TOP_K_RESULTS,
                    "include_raw_content": False,
                },
                timeout=15,
            )
            resp.raise_for_status()
            self.tool_call_counts += 1
            raw_results = resp.json().get("results", [])

            if not raw_results:
                return json.dumps(
                    [{"query": q, "gl": gl, "pages": [], "text_block": ["No results found."], "api_snippets": []}],
                    ensure_ascii=False,
                )

            all_passages: List[str] = []
            api_snippets: List[str] = []  # Tavily content — always collected as guaranteed evidence
            page_info: List[Dict[str, Any]] = []
            successful_count = 0

            for r in raw_results:
                url = r.get("url", "")
                content = r.get("content", "")
                title = r.get("title", "")

                # Always store Tavily's content snippet
                if content:
                    api_snippets.append(content)

                # Try full page crawl first
                if url and successful_count < MAX_SUCCESSFUL_PAGES:
                    fetched = self._fetch(url)
                    crawl_ok = (
                        "error" not in fetched
                        and fetched.get("cleaned", "").strip() != "[content-extraction-failed]"
                    )
                    if crawl_ok:
                        passages = _split_passages(fetched["cleaned"])
                        if passages and any(p.strip() for p in passages):
                            all_passages.extend(passages)
                            page_info.append({"title": fetched["title"] or title, "link": url, "source": "crawled"})
                            successful_count += 1
                            continue

                # Crawl failed — use Tavily's content as passage source
                if content:
                    logging.info(f"[TavilySearch] Crawl failed for {url}, using Tavily API content.")
                    all_passages.extend(_split_passages(content, max_chars=2000, min_chars=200))
                    page_info.append({"title": title, "link": url, "source": "api_snippet"})

            passages_set: List[str] = []
            for claim in claims:
                passages_set.extend(_top_passages(claim, all_passages))
            text_block = list(set(passages_set)) or all_passages[:3]

            results = [{
                "query": q,
                "gl": gl,
                "pages": page_info,
                "text_block": text_block,
                "api_snippets": api_snippets,  # always present for evaluator fallback
            }]
            return json.dumps(results, ensure_ascii=False)
        except Exception as outer:
            error_msg = str(outer)
            if "400 Client Error" in error_msg:
                raise RuntimeError(f"Tavily API 400 Bad Request error - terminating interview: {outer}") from outer
            return json.dumps([{"query": q, "gl": gl, "text_block": f"Search failure: {outer}", "api_snippets": []}], ensure_ascii=False)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "tavily_search",
                "description": (
                    "Given a factual claim, run a Tavily search with query `q` and geolocation `gl`, "
                    "and return pre-extracted content snippets as a JSON string. "
                    "Tavily is optimized for AI fact-verification tasks."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "q": {
                            "type": "string",
                            "description": "Search query for fact verification. Do not include quotation marks.",
                        },
                        "gl": {
                            "type": "string",
                            "description": "Geolocation country code (e.g., 'us', 'uk', 'kr') to tailor search results.",
                        },
                    },
                    "required": ["q", "gl"],
                },
            },
        }

    def calculate_cost(self) -> float:
        # Tavily pricing: ~$0.01 per API credit (1 search = 1 credit)
        cost_per_query = 0.01
        return self.tool_call_counts * cost_per_query
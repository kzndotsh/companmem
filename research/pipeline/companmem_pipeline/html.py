"""HTML to plaintext and a cheap quality gate for prose pages."""

from __future__ import annotations

import html as html_lib
import re


def clean_html(raw: str) -> str:
    """Convert raw HTML to plaintext."""
    text = raw
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<(?:br|hr|/p|/div|/tr|/li|/h[1-6])[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\[citation needed\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[edit\]", "", text, flags=re.IGNORECASE)
    text = text.replace("Ã©", "é").replace("Ã±", "ñ").replace("Ã³", "ó")
    text = text.replace("â€™", "'").replace('â€"', "—").replace("â€œ", '"').replace("â€\x9d", '"')
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" +\n", "\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text.strip()


def quality_score(text: str) -> dict[str, int | float | bool]:
    """Word/prose metrics. HTML docs use this; issue JSON and source files do not."""
    words = text.split()
    lines = [line for line in text.split("\n") if line.strip()]
    prose_lines = [line for line in lines if len(line.split()) > 5]
    return {
        "word_count": len(words),
        "line_count": len(lines),
        "prose_ratio": len(prose_lines) / max(len(lines), 1),
        "is_low_quality": (
            len(words) < 50
            or len(prose_lines) == 0
            or (len(prose_lines) < 3 and len(words) < 200)
        ),
    }

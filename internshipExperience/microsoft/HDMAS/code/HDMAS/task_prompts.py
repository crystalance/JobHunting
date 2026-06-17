"""
Benchmark-specific task prompts appended to the system prompt
via the `task_prompt` parameter.
"""

# ── Global WideSearch prompt ──────────────────────────────────────────
WIDESEARCH_GLOBAL = (
    "Every data cell in this task is publicly available on the web — treat "
    "\"Not found\" as a last resort, not a default.\n\n"
    "**Language-aware search:** When the user's query is in a non-English language, "
    "you MUST primarily search in that language. "
    "Only fall back to English sources when native-language search yields no results.\n\n"
    "When a search doesn't return what you need, don't give up — vary your angle:\n"
    "- Rephrase the query with synonyms, abbreviations, or the entity's official name.\n"
    "- Search for a broader list/table that includes your target "
    "(e.g., search for the full ranking table instead of one entity's rank).\n"
    "- Try different source types: official sites, Wikipedia, aggregator databases, "
    "PDF annual reports, news articles.\n"
    "- Use site-specific search (e.g., `site:nps.gov` or `site:stats.gov.cn`) "
    "when you know which organization owns the data.\n\n"
    "If you found data for most items but a few are missing, go back and search "
    "specifically for those missing ones — they almost certainly exist somewhere. "
    "Think about what kind of source would have this data and target it directly."
)

# ── Per-case hints ────────────────────────────────────────────────────
# One-line targeted hints for specific WideSearch instances.
# Appended after the global WIDESEARCH prompt when the instance_id matches.
WIDESEARCH_PER_CASE: dict[str, str] = {
    "ws_en_006": "For UK concerts, use constituent country names (England/Scotland/Wales/Northern Ireland), NOT 'United Kingdom' or 'UK'.",
    "ws_en_069": "List ALL directors including co-directors, separated by commas.",
    "ws_en_014": "Double-check that the Rank column matches the official ranking exactly; swapping closely-ranked entries is a common error.",
    "ws_en_068": "Use the WORLDWIDE first edition (often the UK edition), not the US edition, for publisher and publication date.",
    "ws_en_041": "Include full dual/multiple nationality (e.g. 'australian-british'), not just one citizenship.",
}

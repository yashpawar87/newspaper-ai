from anthropic import Anthropic

from app.config import settings

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


SUMMARY_PROMPT = """You are writing a short summary of a news article for a news aggregator.

Rules:
- 3 to 4 sentences, capturing the key facts (who, what, when, where, and why it matters).
- Write entirely in your own words. Do not copy phrases or sentence structure from the source.
- Stick to what the article states. Do not add opinion, speculation, or outside context.
- If the article covers a developing/breaking story, note that details may still be developing.
- Output only the summary text. No preamble, no headers, no quotation marks.

Article title: {title}

Article text:
{text}"""


def summarize_article(title: str, full_text: str, max_input_chars: int = 6000) -> str | None:
    """
    Returns a short original-wording summary of the scraped article, or
    None if the summarization call fails for any reason (the caller
    should leave the article teaser-only in that case rather than block
    the enrichment pipeline on a single failure).
    """
    if not full_text:
        return None

    truncated = full_text[:max_input_chars]

    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": SUMMARY_PROMPT.format(title=title, text=truncated),
                }
            ],
        )
        return response.content[0].text.strip()
    except Exception:
        return None

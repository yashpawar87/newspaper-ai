from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


def is_scraping_allowed(url: str, user_agent: str) -> bool:
    """
    Checks robots.txt for the given URL's domain before scraping.

    Fails closed: if robots.txt can't be fetched or parsed for any reason,
    this returns False rather than assuming permission. Combined with the
    per-source `scraping_allowed` flag (set manually after a ToS review),
    this is a second, automated line of defense — not a substitute for
    actually reading each source's terms.
    """
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return False

"""
MkDocs Macros Plugin for displaying custom link cards (Optimized Async Version).
Features:
- Asynchronous SVG content fetching
- Connection pooling and caching
- Domain processing optimization
- URL normalization and validation
- SVG path parsing and caching
- Customizable card layout with SVG/image support
"""

from typing import Optional, Dict, Tuple
from urllib.parse import urlparse
import asyncio
from functools import lru_cache
import httpx
from mkdocs_macros.plugin import MacrosPlugin

from .debug_logger import DebugLogger


async def get_client() -> httpx.AsyncClient:
    """
    Create a configured httpx AsyncClient with optimized connection settings.

    Returns:
        httpx.AsyncClient: Client configured with:
            - 10 second timeout
            - Maximum 5 keepalive connections
            - Maximum 10 total connections
            - Connection pooling enabled
    """
    return httpx.AsyncClient(
        timeout=10.0,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    )


# Global cache for SVG content
SVG_CACHE: Dict[str, Optional[str]] = {}
"""
Cache structure for SVG content:
{
    "url_or_cache_key": svg_content | None
}
Keys can be either:
- Full URLs for direct content lookup
- Formatted cache keys (user_id/gist_id/filename) for Gist content
"""


@lru_cache(maxsize=100)
def parse_svg_path(svg_path: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse and validate custom SVG path format with caching.

    Args:
        svg_path (str): Path in format "user_id/gist_id/filename"

    Returns:
        Optional[Tuple[str, str, str]]: (user_id, gist_id, filename) if valid, None if invalid
    """
    parts = svg_path.split("/")
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


async def get_gist_content(
    user_id: str,
    gist_id: str,
    filename: str,
    logger: DebugLogger,
    client: httpx.AsyncClient,
) -> Optional[str]:
    """
    Asynchronously fetch and cache content from a Gist.

    Args:
        user_id (str): GitHub user ID
        gist_id (str): Gist ID
        filename (str): Target filename
        logger (DebugLogger): Debug logger instance
        client (httpx.AsyncClient): Async HTTP client

    Returns:
        Optional[str]: SVG content if successful, None on failure
    """
    cache_key = f"{user_id}/{gist_id}/{filename}"
    if cache_key in SVG_CACHE:
        logger.log(f"Using cached Gist content for {cache_key}")
        return SVG_CACHE[cache_key]

    logger.log(f"Fetching Gist: User={user_id}, ID={gist_id}, File={filename}")
    try:
        url = f"https://gist.githubusercontent.com/{user_id}/{gist_id}/raw/{filename}"
        response = await client.get(url)
        if response.status_code == 200:
            SVG_CACHE[cache_key] = response.text
            return response.text
        logger.log(f"Gist fetch failed: {response.status_code}")
        SVG_CACHE[cache_key] = None
        return None
    except Exception as e:
        logger.log(f"Gist fetch error: {e}")
        SVG_CACHE[cache_key] = None
        return None


async def get_svg_content(
    url: str, logger: DebugLogger, client: httpx.AsyncClient
) -> Optional[str]:
    """
    Get SVG content based on URL with caching support.

    Args:
        url (str): Target URL to process
        logger (DebugLogger): Debug logger instance
        client (httpx.AsyncClient): Async HTTP client

    Returns:
        Optional[str]: SVG content if found and fetched successfully, None otherwise
    """
    if url in SVG_CACHE:
        logger.log(f"Using cached SVG for URL: {url}")
        return SVG_CACHE[url]

    logger.log(f"Detecting SVG for URL: {url}")
    svg_content = None

    if "github.com" in url:
        logger.log("Using GitHub SVG")
        svg_content = await get_gist_content(
            "7rikazhexde",
            "d418315080179e7c1bd9a7a4366b81f6",
            "github-cutom-icon.svg",
            logger,
            client,
        )
    elif "hatenablog.com" in url:
        logger.log("Using Hatena Blog SVG")
        svg_content = await get_gist_content(
            "7rikazhexde",
            "1b1079ee3793f9223173347b0bc6ab3b",
            "hatenablog-logotype.svg",
            logger,
            client,
        )

    SVG_CACHE[url] = svg_content
    return svg_content


@lru_cache(maxsize=1000)
def extract_domain_for_display(url: str) -> str:
    """
    Extract and format domain portion from URL with caching.

    Args:
        url (str): Full URL to process

    Returns:
        str: Formatted domain name for display
    """
    parsed = urlparse(url)
    if parsed.netloc:
        for domain in ("github.com", "hatenablog.com"):
            if domain in parsed.netloc:
                return parsed.netloc
        return parsed.netloc
    return url


@lru_cache(maxsize=1000)
def clean_url(url: str) -> str:
    """
    Normalize URL by handling duplicated and trailing slashes with caching.

    Args:
        url (str): Input URL to normalize

    Returns:
        str: Normalized URL string
    """
    clean = url
    while "//" in clean[8:]:
        clean = clean.replace("//", "/")
    return clean.rstrip("/")


async def create_link_card(
    url: str,
    title: str,
    description: Optional[str] = None,
    image_path: Optional[str] = None,
    domain: Optional[str] = None,
    external: bool = False,
    svg_path: Optional[str] = None,
    env: Optional[MacrosPlugin] = None,
) -> str:
    """
    Create a customized link card with optimized async processing.

    Args:
        url (str): Target URL
        title (str): Card title
        description (Optional[str]): Card description text
        image_path (Optional[str]): Custom image path
        domain (Optional[str]): Override domain display
        external (bool): External link flag
        svg_path (Optional[str]): Custom SVG path in "user_id/gist_id/filename" format
        env (Optional[MacrosPlugin]): MkDocs macro environment

    Returns:
        str: Rendered HTML for the link card
    """
    logger = DebugLogger.create_logger("link_card", env)
    logger.log("Creating link card", {"url": url, "title": title})

    if not title:
        logger.log("Error: Title is required")
        raise ValueError("`title` is required for creating a link card.")

    clean_target_url = clean_url(url)
    display_domain = domain or extract_domain_for_display(url)
    description = description or ""

    base_url = env.conf.get("site_url", "") if env and hasattr(env, "conf") else ""

    final_image_path = ""
    if not (external and not image_path):
        default_image = "assets/img/site.png"
        final_image_path = image_path or f"{base_url.rstrip('/')}/{default_image}"
        logger.log(f"Image path: {final_image_path}")

    svg_content = None
    async with await get_client() as client:
        if svg_path:
            logger.log(f"Using custom SVG path: {svg_path}")
            parsed_path = parse_svg_path(svg_path)
            if not parsed_path:
                logger.log("Error: Invalid SVG path format")
                return f'''
<div class="custom-link-card" onclick="window.location='{clean_target_url}'" role="link" tabindex="0">
    <div class="custom-link-card-content">
        <div class="custom-link-card-title" aria-label="{title}">{title}</div>
        <div class="custom-link-card-description">Error: Invalid SVG path format</div>
        <a href="{clean_target_url}" class="custom-link-card-domain">{display_domain}</a>
    </div>
</div>
'''
            user_id, gist_id, filename = parsed_path
            svg_content = await get_gist_content(
                user_id, gist_id, filename, logger, client
            )
        else:
            svg_content = await get_svg_content(clean_target_url, logger, client)

    svg_html = ""
    if svg_content:
        svg_html = svg_content.replace('fill="#333"', 'class="svg-path"').replace(
            'fill="black"', 'class="svg-path"'
        )

    html = f'''
<div class="custom-link-card" onclick="window.location='{
        clean_target_url
    }'" role="link" tabindex="0">
    <div class="custom-link-card-content">
        <div class="custom-link-card-title" aria-label="{title}">{title}</div>
        <div class="custom-link-card-description">{description}</div>
        <a href="{clean_target_url}" class="custom-link-card-domain">{
        display_domain
    }</a>
    </div>
    {
        "<div class='custom-link-card-image'>" + svg_html + "</div>"
        if svg_html
        else "<img src='"
        + final_image_path
        + "' alt='"
        + title
        + "' class='custom-link-card-image'>"
        if final_image_path
        else ""
    }
</div>
'''

    logger.log("Link card created successfully")
    return html


def define_env(env: MacrosPlugin) -> None:
    """
    Define link_card macro in MkDocs macro environment.

    Args:
        env (MacrosPlugin): MkDocs macro plugin environment
    """

    async def async_link_card(
        url: str,
        title: str,
        description: Optional[str] = None,
        image_path: Optional[str] = None,
        domain: Optional[str] = None,
        external: bool = False,
        svg_path: Optional[str] = None,
    ) -> str:
        """
        Async implementation of link card creation.

        Args:
            url (str): Target URL
            title (str): Card title
            description (Optional[str]): Card description
            image_path (Optional[str]): Custom image path
            domain (Optional[str]): Override domain display
            external (bool): External link flag
            svg_path (Optional[str]): Custom SVG path

        Returns:
            str: Rendered HTML for the link card
        """
        return await create_link_card(
            url=url,
            title=title,
            description=description,
            image_path=image_path,
            domain=domain,
            external=external,
            svg_path=svg_path,
            env=env,
        )

    def sync_link_card(*args, **kwargs) -> str:
        """
        Synchronous wrapper for async link card creation.

        Args:
            *args: Positional arguments passed to async_link_card
            **kwargs: Keyword arguments passed to async_link_card

        Returns:
            str: Rendered HTML for the link card
        """
        return asyncio.run(async_link_card(*args, **kwargs))

    env.macro(sync_link_card, "link_card")

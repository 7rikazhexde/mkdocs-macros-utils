"""
MkDocs Macros Plugin for displaying custom link cards.
"""

from typing import Optional
from urllib.parse import urlparse
import requests
from mkdocs_macros.plugin import MacrosPlugin

# Import debug logger
from .debug_logger import DebugLogger


def get_gist_content(gist_id: str, filename: str, logger: DebugLogger) -> Optional[str]:
    """
    Fetch content from a Gist

    Args:
        gist_id (str): Gist ID
        filename (str): Filename
        logger (DebugLogger): Debug logger

    Returns:
        Optional[str]: SVG content or None
    """
    logger.log(f"Fetching Gist content: ID={gist_id}, Filename={filename}")
    try:
        url = f"https://gist.githubusercontent.com/7rikazhexde/{gist_id}/raw/{filename}"
        response = requests.get(url)
        if response.status_code == 200:
            logger.log("Gist content fetched successfully")
            return response.text
        logger.log(f"Failed to fetch Gist content. Status code: {response.status_code}")
        return None
    except Exception as e:
        logger.log(f"Error fetching Gist content: {e}")
        return None


def get_svg_content(url: str, logger: DebugLogger) -> Optional[str]:
    """
    Get appropriate SVG content based on URL

    Args:
        url (str): Target URL
        logger (DebugLogger): Debug logger

    Returns:
        Optional[str]: SVG content or None
    """
    logger.log(f"Detecting SVG for URL: {url}")
    if "github.com" in url:
        logger.log("Using GitHub SVG")
        return get_gist_content(
            "d418315080179e7c1bd9a7a4366b81f6", "github-cutom-icon.svg", logger
        )
    elif "hatenablog.com" in url:
        logger.log("Using Hatena Blog SVG")
        return get_gist_content(
            "1b1079ee3793f9223173347b0bc6ab3b", "hatenablog-logotype.svg", logger
        )
    logger.log("No matching SVG found")
    return None


def extract_domain_for_display(url: str) -> str:
    """
    Extract display domain portion from URL

    Args:
        url (str): Complete URL

    Returns:
        str: Display domain portion
    """
    parsed = urlparse(url)
    if parsed.netloc:
        if "github.com" in parsed.netloc:
            return parsed.netloc
        elif "hatenablog.com" in parsed.netloc:
            return parsed.netloc
        return parsed.netloc
    return url


def clean_url(url: str) -> str:
    """
    Normalize URL (handle trailing slashes, etc.)

    Args:
        url (str): Input URL

    Returns:
        str: Normalized URL
    """
    # Consolidate multiple slashes into one (excluding scheme part)
    while "//" in url[8:]:  # Exclude scheme part (https://)
        url = url.replace("//", "/")
    # Remove trailing slash
    if url.endswith("/"):
        url = url[:-1]
    return url


def create_link_card(
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
    Create a link card

    Args:
        url (str): Target URL
        title (str): Card title
        description (Optional[str], optional): Card description. Defaults to None.
        image_path (Optional[str], optional): Image path. Defaults to None.
        domain (Optional[str], optional): Domain name. Auto-extracted from URL if not specified.
        external (bool, optional): External link flag. Defaults to False.
        svg_path (Optional[str], optional): Custom SVG path. Defaults to None.
        env (Optional[MacrosPlugin], optional): MkDocs macro environment. Defaults to None.

    Returns:
        str: Rendered link card HTML
    """
    logger = DebugLogger.create_logger("link_card", env)
    logger.log("Creating link card", {"url": url, "title": title})

    if not title:
        logger.log("Error: Title is required")
        raise ValueError("`title` is required for creating a link card.")

    # Normalize URL
    clean_target_url = clean_url(url)

    # Determine display domain
    display_domain = domain or extract_domain_for_display(url)
    description = description or ""

    # Determine image path
    if external and not image_path:
        final_image_path = ""
        logger.log("External link without image")
    else:
        final_image_path = image_path or "/assets/img/site.png"
        logger.log(f"Image path: {final_image_path}")

    # Get and process SVG content
    svg_content = None
    if svg_path:
        logger.log(f"Using custom SVG path: {svg_path}")
        svg_content = get_gist_content(
            svg_path.split("/")[0], svg_path.split("/")[1], logger
        )
    else:
        svg_content = get_svg_content(clean_target_url, logger)

    svg_html = ""
    if svg_content:
        svg_html = svg_content.replace('fill="#333"', 'class="svg-path"').replace(
            'fill="black"', 'class="svg-path"'
        )

    # Generate HTML
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
    Define link_card macro in MkDocs macro environment

    Args:
        env (MacrosPlugin): Macro plugin environment
    """

    @env.macro
    def link_card(
        url: str,
        title: str,
        description: Optional[str] = None,
        image_path: Optional[str] = None,
        domain: Optional[str] = None,
        external: bool = False,
        svg_path: Optional[str] = None,
    ) -> str:
        """
        MkDocs macro to create a link card

        Args:
            url (str): Target URL
            title (str): Card title
            description (Optional[str], optional): Card description. Defaults to None.
            image_path (Optional[str], optional): Image path. Defaults to None.
            domain (Optional[str], optional): Domain name. Defaults to None.
            external (bool, optional): External link flag. Defaults to False.
            svg_path (Optional[str], optional): Custom SVG path. Defaults to None.

        Returns:
            str: Rendered link card HTML
        """
        return create_link_card(
            url=url,
            title=title,
            description=description,
            image_path=image_path,
            domain=domain,
            external=external,
            svg_path=svg_path,
            env=env,
        )

"""
MkDocs Macros Plugin for displaying X/Twitter link cards.
"""

from typing import Optional
from mkdocs_macros.plugin import MacrosPlugin
import re

# Import debug logger
from .debug_logger import DebugLogger


def validate_x_twitter_url(url: str, logger: DebugLogger) -> bool:
    """
    Validate X/Twitter tweet page URL

    Args:
        url (str): URL to check
        logger (DebugLogger): Debug logger

    Returns:
        bool: True if URL is valid, False otherwise
    """
    # Check URL patterns
    valid_patterns = [
        r"https?://(?:mobile\.)?twitter\.com/\w+/status/\d+",
        r"https?://(?:mobile\.)?x\.com/\w+/status/\d+",
    ]

    for pattern in valid_patterns:
        if re.match(pattern, url):
            logger.log(f"Valid X/Twitter URL: {url}")
            return True

    logger.log(f"Invalid X/Twitter URL: {url}")
    return False


def standardize_twitter_url(url: str, logger: DebugLogger) -> str:
    """
    Standardize URL to twitter.com format

    Args:
        url (str): Original URL
        logger (DebugLogger): Debug logger

    Returns:
        str: Standardized URL
    """
    # Convert x.com to twitter.com
    standardized_url = url.replace("x.com", "twitter.com")

    logger.log(f"URL standardization: {url} -> {standardized_url}")
    return standardized_url


def create_x_twitter_card(url: str, env: Optional[MacrosPlugin] = None) -> str:
    """
    Generate widget HTML from X tweet URL

    Args:
        url (str): X tweet URL
        env (Optional[MacrosPlugin], optional): MkDocs macro environment

    Returns:
        str: Widget HTML
    """
    # Create debug logger
    logger = DebugLogger.create_logger("x_twitter_card", env)

    logger.log("Creating X/Twitter card", {"url": url})

    # URL validation
    if not validate_x_twitter_url(url, logger):
        logger.log("URL validation failed")
        raise ValueError("Invalid X/Twitter URL")

    # Standardize URL
    url = standardize_twitter_url(url, logger)

    # Generate widget HTML
    html = f"""
    <div class="x-twitter-embed" data-url="{url}">
        <blockquote class="twitter-tweet">
            <a href="{url}"></a>
        </blockquote>
    </div>
    """

    logger.log("X/Twitter card HTML generated successfully")
    return html


def define_env(env: MacrosPlugin) -> None:
    """
    Define x_twitter_card macro in MkDocs macro environment

    Args:
        env (MacrosPlugin): Macro plugin environment
    """

    @env.macro
    def x_twitter_card(url: str) -> str:
        """
        MkDocs macro to generate widget HTML from X tweet URL

        Args:
            url (str): X tweet URL

        Returns:
            str: Widget HTML
        """
        return create_x_twitter_card(url, env)

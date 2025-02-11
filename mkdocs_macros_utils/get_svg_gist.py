"""
MkDocs Macros Plugin for displaying SVG from Gist
"""

from typing import Optional, Dict
import requests
import re
from urllib.parse import urlparse
from mkdocs_macros.plugin import MacrosPlugin
from .debug_logger import DebugLogger


def parse_gist_share_url(url: str, logger: DebugLogger) -> Dict[str, str]:
    """
    Parse a Gist share URL to extract Gist details.

    Args:
        url: The GitHub Gist share URL.
        logger: Debug logger for tracking operations.

    Returns:
        A dictionary containing gist_id and other metadata.

    Raises:
        ValueError: If the URL format is invalid.
    """
    logger.log(f"Parsing Gist URL: {url}")

    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) == 2:
        logger.log(f"Successfully parsed Gist ID: {path_parts[1]}")
        return {"gist_id": path_parts[1]}

    logger.log("Failed to parse Gist URL")
    raise ValueError("Invalid Gist share URL format")


def get_gist_content(gist_id: str, logger: DebugLogger) -> Optional[Dict[str, str]]:
    """
    Fetch content from a Gist using GitHub API.

    Args:
        gist_id: Unique identifier of the Gist.
        logger: Debug logger for tracking operations.

    Returns:
        Dictionary containing SVG file details, or None if retrieval fails.
    """
    try:
        url = f"https://api.github.com/gists/{gist_id}"
        logger.log(f"Fetching Gist content from URL: {url}")

        response = requests.get(url)

        if response.status_code == 200:
            gist_data = response.json()

            # Find the first SVG file
            svg_files = {
                filename: file_data["content"]
                for filename, file_data in gist_data["files"].items()
                if filename.lower().endswith(".svg")
            }

            if not svg_files:
                logger.log("No SVG files found in the Gist")
                return None

            # If multiple SVG files, use the first one
            filename = list(svg_files.keys())[0]
            content = svg_files[filename]

            logger.log(f"SVG file found: {filename}")
            return {"filename": filename, "content": content}

        logger.log(f"Failed to fetch Gist content. Status code: {response.status_code}")
        return None

    except Exception as e:
        logger.log(f"Error fetching Gist content: {e}")
        return None


def process_svg(svg_content: str, filename: str) -> str:
    """
    Process SVG content for display.

    Args:
        svg_content: Original SVG content.
        filename: Filename of the SVG for special handling.

    Returns:
        Processed SVG content with modified attributes.
    """
    # Remove width/height attributes (to be controlled by CSS)
    svg_content = re.sub(r'width="[^"]+"', "", svg_content)
    svg_content = re.sub(r'height="[^"]+"', "", svg_content)

    # Apply the same color treatment as link_card.py
    processed_svg = (
        svg_content.replace('fill="#333"', 'class="custom-link-card-icon"')
        .replace('fill="black"', 'class="custom-link-card-icon"')
        .replace('fill-rule="evenodd"', "")
        .replace('clip-rule="evenodd"', "")
    )

    return processed_svg


def define_env(env: MacrosPlugin) -> None:
    """
    Define svg_gist macro in MkDocs macro environment.

    Args:
        env: MkDocs MacrosPlugin environment.
    """

    @env.macro
    def svg_gist(url: str) -> str:
        """
        Display SVG from a GitHub Gist.

        Args:
            url: Share URL of the Gist containing the SVG.

        Returns:
            Processed SVG wrapped in a div with styling, or an error message.

        Raises:
            ValueError: If no SVG file is found.
        """
        logger = DebugLogger.create_logger("svg_gist", env)
        logger.log(f"Processing SVG Gist: {url}")

        try:
            # Extract gist_id from share URL
            gist_details = parse_gist_share_url(url, logger)

            # Fetch Gist content
            gist_content = get_gist_content(gist_details["gist_id"], logger)

            if not gist_content:
                logger.log("No SVG content found")
                raise ValueError("No SVG content found")

            # Process SVG
            processed_svg = process_svg(
                gist_content["content"], gist_content["filename"]
            )

            # Wrap SVG and set size
            if "hatenablog" in gist_content["filename"]:
                # Style for Hatena Blog logo (display full wide logo)
                style = "display:inline-block; width:180px; height:45px; vertical-align:middle;"
                logger.log("Applying Hatena Blog logo style")
            else:
                # Style for normal icons
                style = "display:inline-block; width:72px; height:72px; vertical-align:middle;"
                logger.log("Applying default icon style")

            wrapped_svg = f'''
                <div class="custom-link-card-image" style="{style}">
                    {processed_svg}
                </div>
            '''

            # Remove line breaks and extra spaces (for table display)
            wrapped_svg = wrapped_svg.replace("\n", " ").replace("  ", " ")

            logger.log("SVG processing completed successfully")
            return wrapped_svg

        except Exception as e:
            logger.log(f"Error processing SVG: {str(e)}")
            raise  # Re-raise the exception instead of returning an error string

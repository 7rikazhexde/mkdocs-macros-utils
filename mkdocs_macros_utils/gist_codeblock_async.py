"""
MkDocs Macros Plugin for fetching and displaying Gist code blocks (Optimized Async Version).
Features:
- Asynchronous Gist content fetching
- Connection pooling and request optimization
- Content and language detection caching
- Robust error handling and logging
"""

from typing import Optional, Tuple, Dict, Any
from functools import lru_cache
import re
import asyncio
import httpx
from mkdocs_macros.plugin import MacrosPlugin
from pathlib import Path
from pygments.lexers import guess_lexer, TextLexer

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


# Global cache for storing Gist metadata and content
GIST_CACHE: Dict[str, Dict[str, Any]] = {}
"""
Cache structure for Gist data:
{
    "gist_url": {
        "raw_url": str,        # Raw content URL
        "filename": str,       # Original filename
        "content": str         # Cached Gist content
    }
}
"""


class GistProcessor:
    """
    Processor for handling Gist operations with optimized caching and async fetching.

    Features:
    - Language detection from filename and content
    - Content caching and retrieval
    - Async Gist info and content fetching
    - Robust error handling

    Attributes:
        logger (DebugLogger): Logger instance for debug output
        lang_map (Dict[str, str]): Mapping of file extensions to language identifiers
    """

    def __init__(self, logger: DebugLogger) -> None:
        """
        Initialize GistProcessor with logger and language mappings.

        Args:
            logger (DebugLogger): Debug logger for operation tracking
        """
        self.logger = logger
        self._initialize_lang_map()

    def _initialize_lang_map(self) -> None:
        """
        Initialize mapping between file extensions and language identifiers.
        Used for syntax highlighting in code blocks.
        """
        self.lang_map = {
            ".sh": "bash",
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".css": "css",
            ".scss": "scss",
            ".html": "html",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".toml": "toml",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".php": "php",
            ".rb": "ruby",
            ".sql": "sql",
            ".md": "markdown",
            ".dockerfile": "dockerfile",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".ps1": "powershell",
            ".psm1": "powershell",
            ".psd1": "powershell",
        }

    async def get_gist_info(
        self, gist_url: str, client: httpx.AsyncClient
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Get Gist information with caching support.

        Args:
            gist_url (str): URL of the Gist
            client (httpx.AsyncClient): Async HTTP client

        Returns:
            Tuple[Optional[str], Optional[str], Optional[str]]:
                (raw_url, filename, error_message)
        """
        if gist_url in GIST_CACHE:
            cache_data = GIST_CACHE[gist_url]
            self.logger.log("Using cached Gist info", gist_url)
            return cache_data["raw_url"], cache_data["filename"], None

        if gist_url.startswith("https://gist.githubusercontent.com/"):
            filename = gist_url.split("/")[-1]
            GIST_CACHE[gist_url] = {"raw_url": gist_url, "filename": filename}
            return gist_url, filename, None

        pattern = r"https://gist\.github\.com/([^/]+)/([a-f0-9]+)"
        match = re.match(pattern, gist_url)

        if not match:
            return None, None, "Invalid Gist URL format"

        username, gist_id = match.groups()

        try:
            response = await client.get(f"https://gist.github.com/{username}/{gist_id}")

            if response.status_code != 200:
                return None, None, f"Failed to fetch Gist: HTTP {response.status_code}"

            raw_button_match = re.search(
                r'href="(/[^/]+/[^/]+/raw/[^"]+)"', response.text
            )

            if raw_button_match:
                raw_path = raw_button_match.group(1)
                raw_url = f"https://gist.githubusercontent.com{raw_path}"
                filename = raw_path.split("/")[-1]

                GIST_CACHE[gist_url] = {"raw_url": raw_url, "filename": filename}
                return raw_url, filename, None

            return None, None, "Could not find raw file URL in Gist"

        except httpx.RequestError as e:
            return None, None, f"Request error: {str(e)}"

    @lru_cache(maxsize=100)
    def detect_language_from_filename(self, filename: str) -> str:
        """
        Detect programming language from filename with caching.

        Args:
            filename (str): Name of the file to analyze

        Returns:
            str: Detected language identifier or 'text' if unknown
        """
        if not filename:
            return "text"

        ext = Path(filename).suffix.lower()
        return self.lang_map.get(ext, "text")

    @lru_cache(maxsize=1000)
    def detect_language_from_content(
        self, content: str, filename: Optional[str] = None
    ) -> str:
        """
        Detect programming language from content and filename with caching.

        Args:
            content (str): Source code content
            filename (Optional[str]): Optional filename for extension-based detection

        Returns:
            str: Detected language identifier or 'text' if unknown
        """
        if filename:
            file_lang = self.detect_language_from_filename(filename)
            if file_lang != "text":
                return file_lang

        try:
            lexer = guess_lexer(content)
            if isinstance(lexer, TextLexer):
                return "text"

            lang_name = lexer.aliases[0] if lexer.aliases else lexer.name.lower()
            return self.convert_pygments_to_markdown_lang(lang_name)
        except Exception:
            return "text"

    @lru_cache(maxsize=100)
    def convert_pygments_to_markdown_lang(self, pygments_name: str) -> str:
        """
        Convert Pygments language identifier to Markdown language identifier with caching.

        Args:
            pygments_name (str): Pygments language name

        Returns:
            str: Corresponding Markdown language identifier or 'text' if unknown
        """
        lang_map = {
            "python": "python",
            "python3": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "bash": "bash",
            "console": "bash",
            "shell": "bash",
            "sh": "bash",
            "ruby": "ruby",
            "php": "php",
            "go": "go",
            "rust": "rust",
        }
        return lang_map.get(pygments_name.lower(), "text")

    async def fetch_gist_content(
        self, url: str, client: httpx.AsyncClient
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch and cache Gist content asynchronously.

        Args:
            url (str): Raw Gist URL
            client (httpx.AsyncClient): Async HTTP client

        Returns:
            Tuple[Optional[str], Optional[str]]: (content, error_message)
        """
        if url in GIST_CACHE and "content" in GIST_CACHE[url]:
            self.logger.log("Using cached content", url)
            return GIST_CACHE[url]["content"], None

        try:
            response = await client.get(url)

            if response.status_code == 200:
                if url not in GIST_CACHE:
                    GIST_CACHE[url] = {}
                GIST_CACHE[url]["content"] = response.text
                return response.text, None

            return None, f"Failed to fetch Gist content: HTTP {response.status_code}"

        except httpx.RequestError as e:
            return None, f"Error fetching Gist content: {str(e)}"


def define_env(env: MacrosPlugin) -> None:
    """
    Define gist_codeblock macro in MkDocs macro environment.

    Args:
        env (MacrosPlugin): MkDocs macro plugin environment
    """
    logger = DebugLogger.create_logger("gist_codeblock", env)
    processor = GistProcessor(logger)

    def sync_gist_codeblock(
        gist_url: str, indent: int = 0, ext: Optional[str] = None
    ) -> str:
        """
        Synchronous wrapper for async Gist processing.

        Args:
            gist_url (str): URL of the Gist
            indent (int, optional): Indentation level. Defaults to 0.
            ext (Optional[str], optional): Force specific language extension. Defaults to None.

        Returns:
            str: Rendered code block or error message
        """
        return asyncio.run(_async_gist_codeblock(gist_url, indent, ext))

    async def _async_gist_codeblock(
        gist_url: str, indent: int = 0, ext: Optional[str] = None
    ) -> str:
        """
        Process Gist URL and generate code block asynchronously.

        Args:
            gist_url (str): URL of the Gist
            indent (int, optional): Indentation level. Defaults to 0.
            ext (Optional[str], optional): Force specific language extension. Defaults to None.

        Returns:
            str: Rendered code block or error message
        """
        logger.log("\n=== Starting new Gist processing ===")

        async with await get_client() as client:
            raw_url, filename, error = await processor.get_gist_info(gist_url, client)
            if error:
                return f"Error: {error}"
            if raw_url is None:
                return "Error: Failed to get raw URL"

            content, error = await processor.fetch_gist_content(raw_url, client)
            if error:
                return f"Error: {error}"
            if content is None:
                return "Error: Failed to fetch content"

            lang = (
                ext
                if ext
                else processor.detect_language_from_content(content, filename)
            )

            content = (
                content.replace("\\$", "$")
                .replace("\\`", "`")
                .replace("\\{", "{")
                .replace("\\}", "}")
            )

            indent_spaces = " " * (4 * indent)
            code_block = [
                "",
                f"{indent_spaces}```{lang}",
                *[f"{indent_spaces}{line}" for line in content.splitlines()],
                f"{indent_spaces}```",
                "",
            ]

            logger.log("=== Gist processing completed ===\n")
            return "\n".join(code_block)

    env.macro(sync_gist_codeblock, "gist_codeblock")

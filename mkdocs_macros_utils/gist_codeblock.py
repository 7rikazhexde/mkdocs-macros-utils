"""
MkDocs Macros Plugin for fetching and displaying Gist code blocks.
"""

from typing import Optional, Tuple, Dict
import re
import requests
from mkdocs_macros.plugin import MacrosPlugin
from pathlib import Path
from pygments.lexers import guess_lexer, TextLexer

# Import debug logger
from .debug_logger import DebugLogger


class GistProcessor:
    """Class for processing Gists"""

    def __init__(self, logger: DebugLogger) -> None:
        self.logger = logger
        # Language and extension mappings
        self.lang_map: Dict[str, str] = {
            # Extension-based mappings
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

    def get_gist_info(
        self, gist_url: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get raw URL and metadata from Gist URL"""
        self.logger.log("Processing URL", gist_url)

        # Return as is if already a raw URL
        if gist_url.startswith("https://gist.githubusercontent.com/"):
            filename = gist_url.split("/")[-1]
            self.logger.log("Already raw URL", filename)
            return gist_url, filename, None

        # Extract username and Gist ID
        pattern = r"https://gist\.github\.com/([^/]+)/([a-f0-9]+)"
        match = re.match(pattern, gist_url)

        if not match:
            self.logger.log("Invalid URL format")
            return None, None, "Invalid Gist URL format"

        username, gist_id = match.groups()
        self.logger.log("Extracted info", f"username={username}, gist_id={gist_id}")

        try:
            # Get information from Gist page
            response = requests.get(f"https://gist.github.com/{username}/{gist_id}")
            if response.status_code != 200:
                return None, None, f"Failed to fetch Gist: HTTP {response.status_code}"

            # Find filename and raw URL
            raw_button_match = re.search(
                r'href="(/[^/]+/[^/]+/raw/[^"]+)"', response.text
            )

            if raw_button_match:
                raw_path = raw_button_match.group(1)
                raw_url = f"https://gist.githubusercontent.com{raw_path}"
                filename = raw_path.split("/")[-1]

                self.logger.log(
                    "Got file info from page", f"filename={filename}, raw_url={raw_url}"
                )
                return raw_url, filename, None

            return None, None, "Could not find raw file URL in Gist"

        except requests.RequestException as e:
            return None, None, f"Request error: {str(e)}"

    def detect_language_from_filename(self, filename: str) -> str:
        """Detect language from filename"""
        if not filename:
            return "text"

        # Extract filename and extension from path
        file_path = Path(filename)
        ext = file_path.suffix.lower()

        # Get language from mapping, default to 'text'
        detected_lang = self.lang_map.get(ext, "text")
        self.logger.log(f"Language from filename: {detected_lang}")
        return detected_lang

    def detect_language_from_content(
        self, content: str, filename: Optional[str] = None
    ) -> str:
        """Detect language from content"""
        # First try to detect language from filename
        if filename:
            file_lang = self.detect_language_from_filename(filename)
            if file_lang != "text":
                self.logger.log("Language detected from filename", file_lang)
                return file_lang

        # Language detection using Pygments
        try:
            lexer = guess_lexer(content)

            # Return 'text' if TextLexer
            if isinstance(lexer, TextLexer):
                self.logger.log("Pygments detected plain text")
                return "text"

            # Use first alias or name of lexer
            lang_name = lexer.aliases[0] if lexer.aliases else lexer.name.lower()
            self.logger.log("Pygments detected language", lang_name)

            return self.convert_pygments_to_markdown_lang(lang_name)

        except Exception as e:
            self.logger.log("Error in language detection", str(e))
            return "text"

    def convert_pygments_to_markdown_lang(self, pygments_name: str) -> str:
        """Convert Pygments language name to Markdown language identifier"""
        lang_map = {
            # Basic language mappings
            "python": "python",
            "python3": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "bash": "bash",
            "console": "bash",
            "shell": "bash",
            "sh": "bash",
            # Add other languages as needed
            "ruby": "ruby",
            "php": "php",
            "go": "go",
            "rust": "rust",
        }

        pygments_name = pygments_name.lower()
        return lang_map.get(pygments_name, "text")

    def fetch_gist_content(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Fetch content from raw Gist URL"""
        self.logger.log("Fetching content from", url)

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content_length = len(response.text)
                self.logger.log(
                    "Content fetched successfully", f"Length: {content_length} chars"
                )
                return response.text, None

            self.logger.log(
                "Failed to fetch content", f"Status code: {response.status_code}"
            )
            return None, f"Failed to fetch Gist content: HTTP {response.status_code}"
        except requests.RequestException as e:
            self.logger.log("Error fetching content", str(e))
            return None, f"Error fetching Gist content: {str(e)}"


def define_env(env: MacrosPlugin) -> None:
    """
    Define gist_codeblock macro in MkDocs macro environment
    """
    # Create debug logger
    logger = DebugLogger.create_logger("gist_codeblock", env)
    processor = GistProcessor(logger)

    @env.macro
    def gist_codeblock(
        gist_url: str, indent: int = 0, ext: Optional[str] = None
    ) -> str:
        """Macro to generate code block from Gist"""
        logger.log("\n=== Starting new Gist processing ===")
        logger.log("Input parameters", f"URL={gist_url}, indent={indent}, ext={ext}")

        # Get raw URL and metadata
        raw_url, filename, error = processor.get_gist_info(gist_url)
        if error:
            logger.log("Error getting Gist info", error)
            return f"Error: {error}"

        if raw_url is None:
            return "Error: Failed to get raw URL"

        logger.log("Got Gist info", f"raw_url={raw_url}, filename={filename}")

        # Get content
        content, error = processor.fetch_gist_content(raw_url)
        if error:
            logger.log("Error fetching content", error)
            return f"Error: {error}"

        if content is None:
            return "Error: Failed to fetch content"

        # Language detection logic
        if ext:
            # Prioritize user-specified extension
            logger.log("Using specified extension", ext)
            lang = ext
        else:
            # Detect language from extension and content
            lang = processor.detect_language_from_content(content, filename)

        logger.log("Final language selection", lang)

        # Unescape special characters
        content = content.replace("\\$", "$")
        content = content.replace("\\`", "`")
        content = content.replace("\\{", "{")
        content = content.replace("\\}", "}")

        # Calculate indentation (4 spaces × level)
        indent_spaces = " " * (4 * indent)

        # Generate code block
        code_block = [
            "",  # Add empty line
            f"{indent_spaces}```{lang}",
            *[f"{indent_spaces}{line}" for line in content.splitlines()],
            f"{indent_spaces}```",
            "",  # Add empty line
        ]

        logger.log("=== Gist processing completed ===\n")
        return "\n".join(code_block)

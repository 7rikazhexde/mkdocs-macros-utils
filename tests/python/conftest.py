"""
Common test configurations and fixtures for MkDocs Macros Utils tests.
This module provides shared test utilities including mock classes and fixtures.
"""

from typing import Any, Callable, Dict, List, Optional, Type
import pytest
from pytest import Config
from mkdocs_macros_utils.debug_logger import DebugLogger
from mkdocs_macros_utils.gist_codeblock import GistProcessor, define_env


class MockMacrosPlugin:
    """Mock class for MkDocs Macros Plugin

    This class simulates the behavior of the MkDocs Macros Plugin for testing purposes.
    It can be configured with custom debug settings and site configuration.
    """

    def __init__(
        self,
        conf: Optional[Dict[str, str]] = None,
        debug_settings: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.conf = conf or {}
        self.default_settings = {
            "extra": {
                "debug": {
                    "gist_codeblock": True,
                    "link_card": True,
                    "x_twitter_card": True,
                }
            }
        }
        self._variables = debug_settings or self.default_settings

    @property
    def variables(self) -> Dict[str, Any]:
        """Get plugin variables"""
        return self._variables

    def macro(self, f: Callable[..., str]) -> Callable[..., str]:
        """Register a macro function

        Args:
            f: Function to register as a macro

        Returns:
            Function: The registered macro function
        """
        macro_name = f.__name__
        setattr(self, macro_name, f)
        return f


@pytest.fixture
def mock_logger() -> DebugLogger:
    """Debug logger fixture for testing

    Returns:
        DebugLogger: An enabled debug logger instance
    """
    return DebugLogger("test", enabled=True)


@pytest.fixture
def mock_env() -> MockMacrosPlugin:
    """Mock environment fixture with default site URL configuration

    Returns:
        MockMacrosPlugin: A configured mock plugin instance
    """
    mock_plugin = MockMacrosPlugin({"site_url": "https://example.com/"})
    return mock_plugin


@pytest.fixture
def env() -> MockMacrosPlugin:
    """MkDocs macro plugin fixture for gist codeblock testing

    Returns:
        MockMacrosPlugin: A configured mock plugin instance with gist_codeblock macro
    """
    plugin = MockMacrosPlugin()
    define_env(plugin)
    return plugin


@pytest.fixture
def processor(mock_logger: DebugLogger) -> GistProcessor:
    """GistProcessor fixture for testing

    Args:
        mock_logger: Debug logger fixture

    Returns:
        GistProcessor: A configured GistProcessor instance
    """
    return GistProcessor(mock_logger)


@pytest.fixture
def mock_response() -> Type[Any]:
    """HTTP response mock fixture

    Returns:
        class: A mock response class that can be instantiated with custom text and status code
    """

    class MockResponse:
        def __init__(self, text: str = "", status_code: int = 200) -> None:
            self.text = text
            self.status_code = status_code
            self._content = text.encode() if isinstance(text, str) else text

    return MockResponse


def pytest_configure(config: Config) -> None:
    """Configure pytest with custom markers

    Args:
        config: Pytest config object
    """
    config.addinivalue_line("markers", "gist: mark a test related to Gist processing")
    config.addinivalue_line(
        "markers", "link_card: mark a test related to link card processing"
    )
    config.addinivalue_line("markers", "debug: mark a test related to debug logging")


def mock_requests_get(
    responses: List[Any], current_response: Optional[Dict[str, int]] = None
) -> Callable[..., Any]:
    """Generate a mock function for requests.get

    Creates a mock function that returns predefined responses in sequence.

    Args:
        responses: List of mock responses to return
        current_response: Dictionary to track response index. Defaults to None.

    Returns:
        function: Mock requests.get function
    """
    if current_response is None:
        current_response = {"index": 0}

    def _mock_get(*args: Any, **kwargs: Any) -> Any:
        response = responses[current_response["index"]]
        current_response["index"] += 1
        return response

    return _mock_get

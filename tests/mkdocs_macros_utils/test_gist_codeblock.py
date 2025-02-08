"""
Tests for Gist codeblock module in MkDocs Macros Utils
"""

from typing import Any, List, Optional, Tuple, Type, cast
from pytest import MonkeyPatch
from pytest_mock import MockerFixture
import requests
from mkdocs_macros_utils.gist_codeblock import GistProcessor
from mkdocs_macros_utils.debug_logger import DebugLogger
from tests import MockMacrosPlugin


# -- Language Detection Tests ------------------------------
def test_detect_language_from_filename(processor: GistProcessor) -> None:
    """Test language detection from various file extensions"""
    test_cases = [
        ("test.py", "python"),
        ("test.js", "javascript"),
        ("test.unknown", "text"),
        ("", "text"),
    ]
    for filename, expected in test_cases:
        assert processor.detect_language_from_filename(filename) == expected


def test_convert_pygments_to_markdown_lang(processor: GistProcessor) -> None:
    """Test Pygments language name conversion to Markdown"""
    test_cases = [("Python", "python"), ("PYTHON3", "python"), ("unknown", "text")]
    for pygments_name, expected in test_cases:
        assert processor.convert_pygments_to_markdown_lang(pygments_name) == expected


def test_detect_language_from_content(processor: GistProcessor) -> None:
    """Test language detection from content with and without filename"""
    test_cases = [
        ("print('hello')", "test.py", "python"),
        ("console.log('hello')", "test.js", "javascript"),
        ("plain text", None, "text"),
    ]
    for content, filename, expected in test_cases:
        assert processor.detect_language_from_content(content, filename) == expected


# -- Gist URL Processing Tests ------------------------------
def test_get_gist_info_raw_url(processor: GistProcessor) -> None:
    """Test processing of already raw Gist URLs"""
    raw_url = "https://gist.githubusercontent.com/user/raw/file.py"
    result_url, filename, error = processor.get_gist_info(raw_url)
    assert filename == "file.py"
    assert error is None
    assert result_url == raw_url


def test_get_gist_info_success(
    monkeypatch: MonkeyPatch, processor: GistProcessor, mock_response: Type[Any]
) -> None:
    """Test successful Gist URL processing"""
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: mock_response(
            '<a href="/user/123456/raw/file.py">Raw</a>'
        ),
    )

    raw_url, filename, error = processor.get_gist_info(
        "https://gist.github.com/user/123456"
    )

    assert error is None
    assert filename == "file.py"
    assert raw_url == "https://gist.githubusercontent.com/user/123456/raw/file.py"


# -- Error Handling Tests ------------------------------
def test_get_gist_info_error_cases(
    monkeypatch: MonkeyPatch, processor: GistProcessor, mock_response: Type[Any]
) -> None:
    """Test various error cases in Gist URL processing"""
    test_cases: List[Tuple[Optional[Tuple[str, int]], str, str]] = [
        (
            ("", 404),
            "https://gist.github.com/user/123456",
            "Failed to fetch Gist: HTTP 404",
        ),
        (
            ("<html>No raw button</html>", 200),
            "https://gist.github.com/user/123456",
            "Could not find raw file URL in Gist",
        ),
        (None, "https://invalid.url", "Invalid Gist URL format"),
    ]

    for response_args, url, expected_error in test_cases:
        if response_args is not None:
            monkeypatch.setattr(
                requests, "get", lambda *args, **kwargs: mock_response(*response_args)
            )

        raw_url, filename, error = processor.get_gist_info(url)
        assert error == expected_error
        assert raw_url is None
        assert filename is None


def test_get_gist_info_request_exception(
    monkeypatch: MonkeyPatch, processor: GistProcessor
) -> None:
    """Test request exception handling"""

    def mock_get(*args: Any, **kwargs: Any) -> None:
        raise requests.RequestException("Connection error")

    monkeypatch.setattr(requests, "get", mock_get)
    raw_url, filename, error = processor.get_gist_info(
        "https://gist.github.com/user/123456"
    )

    assert error == "Request error: Connection error"
    assert raw_url is None
    assert filename is None


# -- Content Fetching Tests ------------------------------
def test_fetch_gist_content_cases(
    monkeypatch: MonkeyPatch, processor: GistProcessor, mock_response: Type[Any]
) -> None:
    """Test various cases of content fetching"""
    test_cases: List[Tuple[Tuple[str, int], Optional[str], Optional[str]]] = [
        (("test content", 200), "test content", None),
        (("", 404), None, "Failed to fetch Gist content: HTTP 404"),
    ]

    for response_args, expected_content, expected_error in test_cases:
        monkeypatch.setattr(
            requests, "get", lambda *args, **kwargs: mock_response(*response_args)
        )

        content, error = processor.fetch_gist_content("https://test.url")
        assert content == expected_content
        assert (error is None) == (expected_error is None)
        if expected_error:
            assert expected_error in str(error)


def test_fetch_gist_content_request_exception(
    monkeypatch: MonkeyPatch, processor: GistProcessor
) -> None:
    """Test exception handling in content fetching"""

    def mock_get(*args: Any, **kwargs: Any) -> None:
        raise requests.RequestException("Connection timeout")

    monkeypatch.setattr(requests, "get", mock_get)
    content, error = processor.fetch_gist_content("https://test.url")

    assert content is None
    assert "Error fetching Gist content: Connection timeout" in str(error)


# -- Language Detection with Lexer Tests ------------------------------
def test_detect_language_from_content_with_lexer(mocker: MockerFixture) -> None:
    """Test language detection using lexer with aliases"""
    logger = DebugLogger("test")
    processor = GistProcessor(logger)

    mock_lexer = mocker.Mock(spec=["aliases", "name"])
    mock_lexer.aliases = ["python"]
    mock_lexer.name = "Python"
    mocker.patch(
        "mkdocs_macros_utils.gist_codeblock.guess_lexer", return_value=mock_lexer
    )
    mocker.patch("mkdocs_macros_utils.gist_codeblock.isinstance", return_value=False)

    result = processor.detect_language_from_content("print('test')", filename=None)
    assert result == "python"


def test_detect_language_from_content_exception_handling(mocker: MockerFixture) -> None:
    """Test exception handling in language detection"""
    logger = DebugLogger("test")
    processor = GistProcessor(logger)

    mocker.patch(
        "mkdocs_macros_utils.gist_codeblock.guess_lexer",
        side_effect=Exception("Test error"),
    )

    result = processor.detect_language_from_content("print('test')", filename=None)
    assert result == "text"


# -- Macro Integration Tests ------------------------------
def test_gist_codeblock_macro_complete(
    monkeypatch: MonkeyPatch, env: MockMacrosPlugin, mock_response: Type[Any]
) -> None:
    """Test complete macro functionality with successful case"""
    responses = [
        mock_response('<a href="/user/123/raw/test.py">Raw</a>'),
        mock_response("def test():\n    return True"),
    ]
    current_response = {"index": 0}

    def mock_get(*args: Any, **kwargs: Any) -> Any:
        response = responses[current_response["index"]]
        current_response["index"] += 1
        return response

    monkeypatch.setattr(requests, "get", mock_get)
    casted_env = cast(Any, env)
    result = casted_env.gist_codeblock("https://gist.github.com/user/123")

    assert "```python" in result
    assert "def test():" in result
    assert "return True" in result


def test_gist_codeblock_with_options(
    monkeypatch: MonkeyPatch, env: MockMacrosPlugin, mock_response: Type[Any]
) -> None:
    """Test macro with indent and extension options"""
    responses = [
        mock_response('<a href="/user/123/raw/test.file">Raw</a>'),
        mock_response("test content"),
    ]
    current_response = {"index": 0}

    def mock_get(*args: Any, **kwargs: Any) -> Any:
        response = responses[current_response["index"]]
        current_response["index"] += 1
        return response

    monkeypatch.setattr(requests, "get", mock_get)
    casted_env = cast(Any, env)
    result = casted_env.gist_codeblock(
        "https://gist.github.com/user/123", indent=1, ext="python"
    )

    assert "    ```python" in result
    assert "    test content" in result


def test_gist_codeblock_error_cases(
    monkeypatch: MonkeyPatch, env: MockMacrosPlugin
) -> None:
    """Test error cases in macro execution"""

    def test_case(mock_get_gist_info: Any, expected_error: str) -> None:
        monkeypatch.setattr(GistProcessor, "get_gist_info", mock_get_gist_info)
        casted_env = cast(Any, env)
        result = casted_env.gist_codeblock("https://gist.github.com/user/123")
        assert expected_error in result

    # Test: raw_url is None
    test_case(lambda *args: (None, None, None), "Error: Failed to get raw URL")

    # Test: error from get_gist_info
    test_case(lambda *args: (None, None, "Test error"), "Error: Test error")


def test_gist_codeblock_raw_url_none(
    monkeypatch: MonkeyPatch, env: MockMacrosPlugin
) -> None:
    """Test specific case where get_gist_info returns None for raw_url"""
    monkeypatch.setattr(
        GistProcessor, "get_gist_info", lambda *args: (None, None, None)
    )
    casted_env = cast(Any, env)
    result = casted_env.gist_codeblock("https://gist.github.com/user/123")
    assert result == "Error: Failed to get raw URL"


def test_gist_codeblock_special_chars(
    monkeypatch: MonkeyPatch, env: MockMacrosPlugin, mock_response: Type[Any]
) -> None:
    """Test handling of special characters in gist content"""
    responses = [
        mock_response('<a href="/user/123/raw/test.py">Raw</a>'),
        mock_response("test\\$var\\`temp\\{\\}"),
    ]
    current_response = {"index": 0}

    def mock_get(*args: Any, **kwargs: Any) -> Any:
        response = responses[current_response["index"]]
        current_response["index"] += 1
        return response

    monkeypatch.setattr(requests, "get", mock_get)
    casted_env = cast(Any, env)
    result = casted_env.gist_codeblock("https://gist.github.com/user/123")

    assert "test$var`temp{}" in result.splitlines()
    assert "```python" in result


def test_gist_codeblock_multiline_content(
    monkeypatch: MonkeyPatch, env: MockMacrosPlugin, mock_response: Type[Any]
) -> None:
    """Test handling of multiline content with indentation"""
    responses = [
        mock_response('<a href="/user/123/raw/test.py">Raw</a>'),
        mock_response("line1\nline2\nline3"),
    ]
    current_response = {"index": 0}

    def mock_get(*args: Any, **kwargs: Any) -> Any:
        response = responses[current_response["index"]]
        current_response["index"] += 1
        return response

    monkeypatch.setattr(requests, "get", mock_get)
    casted_env = cast(Any, env)
    result = casted_env.gist_codeblock("https://gist.github.com/user/123", indent=2)

    result_lines = result.splitlines()
    assert "        ```python" in result_lines
    assert "        line1" in result_lines
    assert "        line2" in result_lines
    assert "        line3" in result_lines
    assert "" in result_lines


def test_fetch_gist_content_failure_with_error(
    monkeypatch: MonkeyPatch, processor: GistProcessor, mock_response: Type[Any]
) -> None:
    """Test content fetch failure with error message"""

    def mock_get(*args: Any, **kwargs: Any) -> Any:
        return mock_response("", status_code=500)

    monkeypatch.setattr(requests, "get", mock_get)
    content, error = processor.fetch_gist_content("https://test.url")

    assert content is None
    assert error == "Failed to fetch Gist content: HTTP 500"


def test_gist_codeblock_content_fetch_error(
    monkeypatch: MonkeyPatch, env: MockMacrosPlugin, mock_response: Type[Any]
) -> None:
    """Test gist_codeblock when fetch_gist_content returns error"""
    responses = [
        mock_response('<a href="/user/123/raw/test.py">Raw</a>'),
        mock_response("", status_code=500),
    ]
    current_response = {"index": 0}

    def mock_get(*args: Any, **kwargs: Any) -> Any:
        response = responses[current_response["index"]]
        current_response["index"] += 1
        return response

    monkeypatch.setattr(requests, "get", mock_get)
    casted_env = cast(Any, env)
    result = casted_env.gist_codeblock("https://gist.github.com/user/123")

    assert result == "Error: Failed to fetch Gist content: HTTP 500"


def test_gist_codeblock_fetch_content_returns_none(
    monkeypatch: MonkeyPatch, env: MockMacrosPlugin
) -> None:
    """Test case where fetch_gist_content returns None for content"""

    def mock_get_gist_info(*args: Any) -> Tuple[str, str, None]:
        return "raw_url", "test.py", None

    def mock_fetch_content(*args: Any) -> Tuple[None, None]:
        return None, None  # content is None and error is also None

    monkeypatch.setattr(GistProcessor, "get_gist_info", mock_get_gist_info)
    monkeypatch.setattr(GistProcessor, "fetch_gist_content", mock_fetch_content)

    casted_env = cast(Any, env)
    result = casted_env.gist_codeblock("https://gist.github.com/user/123")
    assert result == "Error: Failed to fetch content"

"""
Tests for Link Card module in MkDocs Macros Utils.
This module tests the functionality for creating and managing link cards,
including URL processing, SVG content retrieval, and card generation.
"""

from typing import Any, cast, Optional
import pytest
from pytest import MonkeyPatch
import requests
from mkdocs_macros_utils.link_card import (
    get_gist_content,
    get_svg_content,
    extract_domain_for_display,
    clean_url,
    create_link_card,
    define_env,
)
from mkdocs_macros_utils.debug_logger import DebugLogger
from tests import MockMacrosPlugin


# -- Gist Content Tests ------------------------------
def test_get_gist_content_success(
    monkeypatch: MonkeyPatch, mock_logger: DebugLogger
) -> None:
    """Test successful retrieval of Gist content"""

    def mock_get(*args: Any, **kwargs: Any) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        response._content = b"Test content"
        return response

    monkeypatch.setattr(requests, "get", mock_get)

    result = get_gist_content("testuser", "testgist", "testfile.txt", mock_logger)
    assert result == "Test content"


def test_get_gist_content_failure(
    monkeypatch: MonkeyPatch, mock_logger: DebugLogger
) -> None:
    """Test Gist content retrieval failure with 404 status"""

    def mock_get(*args: Any, **kwargs: Any) -> requests.Response:
        response = requests.Response()
        response.status_code = 404
        return response

    monkeypatch.setattr(requests, "get", mock_get)

    result = get_gist_content("testuser", "testgist", "testfile.txt", mock_logger)
    assert result is None


def test_get_gist_content_exception(
    monkeypatch: MonkeyPatch, mock_logger: DebugLogger
) -> None:
    """Test Gist content retrieval with network error"""

    def mock_get(*args: Any, **kwargs: Any) -> None:
        raise requests.RequestException("Network error")

    monkeypatch.setattr(requests, "get", mock_get)

    result = get_gist_content("testuser", "testgist", "testfile.txt", mock_logger)
    assert result is None


# -- SVG Content Tests ------------------------------
def test_get_svg_content(monkeypatch: MonkeyPatch, mock_logger: DebugLogger) -> None:
    """Test SVG content retrieval for different domains"""

    def mock_get_gist_content(
        user_id: str, gist_id: str, filename: str, logger: DebugLogger
    ) -> str:
        return "<svg>Test</svg>"

    monkeypatch.setattr(
        "mkdocs_macros_utils.link_card.get_gist_content", mock_get_gist_content
    )

    # Test different domain types
    github_result = get_svg_content("https://github.com/test", mock_logger)
    assert github_result == "<svg>Test</svg>"

    hatena_result = get_svg_content("https://hatenablog.com/test", mock_logger)
    assert hatena_result == "<svg>Test</svg>"

    unknown_result = get_svg_content("https://example.com", mock_logger)
    assert unknown_result is None


# -- Domain Extraction Tests ------------------------------
def test_extract_domain_for_display() -> None:
    """Test domain extraction from various URL formats"""
    test_cases = [
        ("https://github.com/user/repo", "github.com"),
        ("https://blog.hatena.ne.jp/user", "blog.hatena.ne.jp"),
        ("https://example.com/path", "example.com"),
        ("invalid_url", "invalid_url"),
    ]

    for url, expected in test_cases:
        assert extract_domain_for_display(url) == expected


def test_extract_domain_for_display_additional_cases() -> None:
    """Test additional cases for domain extraction, particularly hatenablog.com domains"""
    test_cases = [
        # Specific test for hatenablog.com domain handling
        ("https://custom.hatenablog.com/path", "custom.hatenablog.com"),
        ("https://another.hatenablog.com", "another.hatenablog.com"),
        # Additional general cases
        ("https://example.com/path", "example.com"),
        ("invalid-url", "invalid-url"),
    ]

    for url, expected in test_cases:
        result = extract_domain_for_display(url)
        assert result == expected, f"Failed for URL: {url}"


# -- URL Cleaning Tests ------------------------------
def test_clean_url() -> None:
    """Test URL cleaning for standard cases"""
    test_cases = [
        (
            "https://example.com//path//to//resource/",
            "https://example.com/path/to/resource",
        ),
        ("https://example.com/", "https://example.com"),
        ("https://example.com", "https://example.com"),
    ]

    for input_url, expected in test_cases:
        result = clean_url(input_url)
        assert result == expected, f"Failed for input: {input_url}"


def test_clean_url_edge_cases() -> None:
    """Test URL cleaning for edge cases"""
    edge_cases = [
        ("http://example.com", "http://example.com"),
        ("https://example.com////", "https://example.com"),
        ("https://example.com///////path", "https://example.com/path"),
    ]

    for input_url, expected in edge_cases:
        result = clean_url(input_url)
        assert result == expected, f"Failed for input: {input_url}"


def test_clean_url_no_scheme() -> None:
    """Test URL cleaning for URLs without scheme"""
    test_cases = [
        ("example.com", "example.com"),
        ("example.com/path", "example.com/path"),
        ("", ""),
        ("///", "///"),
    ]

    for input_url, expected in test_cases:
        result = clean_url(input_url)
        assert result == expected, f"Failed for input: {input_url}"


# -- Link Card Creation Tests ------------------------------
def test_create_link_card_svg_path(
    monkeypatch: MonkeyPatch, mock_env: MockMacrosPlugin
) -> None:
    """Test link card creation with custom SVG path"""

    def mock_get_gist_content(*args: Any, **kwargs: Any) -> str:
        return "<svg>Custom</svg>"

    monkeypatch.setattr(
        "mkdocs_macros_utils.link_card.get_gist_content", mock_get_gist_content
    )

    result = create_link_card(
        url="https://example.com",
        title="SVG Path Test",
        svg_path="user/gistid/file.svg",
        env=mock_env,
    )

    assert "SVG Path Test" in result
    assert "Custom" in result


def test_create_link_card_invalid_svg_path(mock_env: MockMacrosPlugin) -> None:
    """Test link card creation with invalid SVG path format"""
    result = create_link_card(
        url="https://example.com",
        title="Invalid SVG Path Test",
        svg_path="invalid_path",
        env=mock_env,
    )

    assert "Invalid SVG Path Test" in result
    assert "Invalid SVG path format" in result


def test_create_link_card_missing_title() -> None:
    """Test link card creation without a required title"""
    with pytest.raises(
        ValueError, match="`title` is required for creating a link card."
    ):
        create_link_card(url="https://example.com", title="")


def test_create_link_card_external_no_image(mock_env: MockMacrosPlugin) -> None:
    """Test external link card creation without an image"""
    result = create_link_card(
        url="https://example.com",
        title="External Link Test",
        external=True,
        env=mock_env,
    )

    assert "External Link Test" in result
    assert "image" not in result


def test_create_link_card_no_env() -> None:
    """Test link card creation without environment configuration"""
    result = create_link_card(url="https://example.com", title="No Env Test")

    assert "No Env Test" in result
    assert "https://example.com" in result


def test_create_link_card_with_absolute_image_path(mock_env: MockMacrosPlugin) -> None:
    """Test link card creation with absolute image path"""
    result = create_link_card(
        url="https://example.com",
        title="Absolute Image Path Test",
        image_path="https://example.com/custom/image.png",
        env=mock_env,
    )

    assert "Absolute Image Path Test" in result
    assert "https://example.com/custom/image.png" in result


def test_create_link_card_full_options(
    monkeypatch: MonkeyPatch, mock_env: MockMacrosPlugin
) -> None:
    """Test link card creation with all available options"""

    def mock_get_svg_content(*args: Any, **kwargs: Any) -> Optional[str]:
        url = args[0]
        if "github.com" in url:
            return "<svg>Test</svg>"
        return None

    monkeypatch.setattr(
        "mkdocs_macros_utils.link_card.get_svg_content", mock_get_svg_content
    )

    result = create_link_card(
        url="https://test.com/test",
        title="Full Test",
        description="Test Description",
        image_path="/custom/image.png",
        domain="custom.domain",
        external=True,
        env=mock_env,
    )

    assert "Full Test" in result
    assert "Test Description" in result
    assert "custom.domain" in result
    assert "<img" in result
    assert "src='https://example.com/custom/image.png'" in result
    assert "class='custom-link-card-image'" in result
    assert "alt='Full Test'" in result


# -- Environment and Macro Tests ------------------------------
def test_define_env() -> None:
    """Test environment setup and macro registration"""
    mock_env = MockMacrosPlugin()
    define_env(mock_env)
    assert hasattr(mock_env, "link_card")


def test_link_card_macro(mock_env: MockMacrosPlugin) -> None:
    """Test the link_card macro functionality"""
    define_env(mock_env)

    # Type cast to tell mypy that the attribute exists after define_env
    env = cast(Any, mock_env)
    result = env.link_card(
        url="https://example.com",
        title="Macro Test",
        description="Testing the macro directly",
        image_path="/test.png",
        domain="custom.domain",
        external=True,
        svg_path="user/gist/file.svg",
    )

    assert "Macro Test" in result
    assert "Testing the macro directly" in result
    assert "custom.domain" in result
    assert "https://example.com" in result

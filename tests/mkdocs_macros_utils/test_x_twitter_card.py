"""
Tests for X/Twitter Card module in MkDocs Macros Utils.
This module tests the functionality for creating and managing X/Twitter cards,
including URL validation, standardization, and card generation.
"""

from typing import Any, cast
import pytest
from mkdocs_macros_utils.x_twitter_card import (
    validate_x_twitter_url,
    standardize_twitter_url,
    create_x_twitter_card,
    define_env,
)
from mkdocs_macros_utils.debug_logger import DebugLogger
from tests import MockMacrosPlugin


# -- URL Validation Tests ------------------------------


def test_validate_x_twitter_url_valid_cases(mock_logger: DebugLogger) -> None:
    """Test URL validation with valid X/Twitter URLs"""
    valid_urls = [
        "https://twitter.com/user/status/123456789",
        "https://mobile.twitter.com/user/status/123456789",
        "https://x.com/user/status/123456789",
        "https://mobile.x.com/user/status/123456789",
        "http://twitter.com/user/status/123456789",
        "http://x.com/user/status/123456789",
    ]

    for url in valid_urls:
        assert validate_x_twitter_url(url, mock_logger) is True


def test_validate_x_twitter_url_invalid_cases(mock_logger: DebugLogger) -> None:
    """Test URL validation with invalid URLs"""
    invalid_urls = [
        "https://twitter.com/user",
        "https://x.com/user",
        "https://example.com",
        "invalid_url",
        "https://twitter.com/status/123456789",
        "https://x.com/status/",
        "",
        "https://twitter.com/user/status/",
        "https://x.com/user/status/abc",
    ]

    for url in invalid_urls:
        assert validate_x_twitter_url(url, mock_logger) is False


# -- URL Standardization Tests ------------------------------


def test_standardize_twitter_url(mock_logger: DebugLogger) -> None:
    """Test URL standardization from x.com to twitter.com"""
    test_cases = [
        (
            "https://x.com/user/status/123456789",
            "https://twitter.com/user/status/123456789",
        ),
        (
            "https://mobile.x.com/user/status/123456789",
            "https://mobile.twitter.com/user/status/123456789",
        ),
        (
            "https://twitter.com/user/status/123456789",
            "https://twitter.com/user/status/123456789",
        ),
        (
            "http://x.com/user/status/123456789",
            "http://twitter.com/user/status/123456789",
        ),
    ]

    for input_url, expected_url in test_cases:
        result = standardize_twitter_url(input_url, mock_logger)
        assert result == expected_url, f"Failed for input: {input_url}"


# -- Card Creation Tests ------------------------------


def test_create_x_twitter_card_valid_url(mock_env: MockMacrosPlugin) -> None:
    """Test X/Twitter card creation with valid URL"""
    url = "https://twitter.com/user/status/123456789"
    result = create_x_twitter_card(url, mock_env)

    assert '<div class="x-twitter-embed"' in result
    assert '<blockquote class="twitter-tweet"' in result
    assert f'data-url="{url}"' in result
    assert f'<a href="{url}"></a>' in result


def test_create_x_twitter_card_standardize_url(mock_env: MockMacrosPlugin) -> None:
    """Test X/Twitter card creation with x.com URL"""
    x_url = "https://x.com/user/status/123456789"
    twitter_url = "https://twitter.com/user/status/123456789"

    result = create_x_twitter_card(x_url, mock_env)

    assert f'data-url="{twitter_url}"' in result
    assert f'<a href="{twitter_url}"></a>' in result


def test_create_x_twitter_card_invalid_url(mock_env: MockMacrosPlugin) -> None:
    """Test X/Twitter card creation with invalid URL"""
    with pytest.raises(ValueError, match="Invalid X/Twitter URL"):
        create_x_twitter_card("https://example.com", mock_env)


def test_create_x_twitter_card_no_env() -> None:
    """Test X/Twitter card creation without environment"""
    url = "https://twitter.com/user/status/123456789"
    result = create_x_twitter_card(url)

    assert '<div class="x-twitter-embed"' in result
    assert '<blockquote class="twitter-tweet"' in result
    assert f'data-url="{url}"' in result


# -- Environment and Macro Tests ------------------------------


def test_define_env() -> None:
    """Test environment setup and macro registration"""
    mock_env = MockMacrosPlugin()
    define_env(mock_env)
    assert hasattr(mock_env, "x_twitter_card")


def test_x_twitter_card_macro() -> None:
    """Test the x_twitter_card macro functionality"""
    mock_env = MockMacrosPlugin()
    define_env(mock_env)

    # Type cast to tell mypy that the attribute exists after define_env
    env = cast(Any, mock_env)
    url = "https://twitter.com/user/status/123456789"
    result = env.x_twitter_card(url)

    assert '<div class="x-twitter-embed"' in result
    assert '<blockquote class="twitter-tweet"' in result
    assert f'data-url="{url}"' in result

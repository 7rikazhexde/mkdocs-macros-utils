"""
Tests for Debug Logger module in MkDocs Macros Utils
"""

import pytest
from _pytest.logging import LogCaptureFixture
from tests import MockMacrosPlugin
from mkdocs_macros_utils.debug_logger import DebugLogger


@pytest.mark.debug
def test_create_logger_without_env() -> None:
    """Test creating a logger without an environment"""
    logger = DebugLogger.create_logger("test_module")
    assert isinstance(logger, DebugLogger)
    assert logger.enabled is False


@pytest.mark.debug
def test_create_logger_with_env(mock_env: MockMacrosPlugin) -> None:
    """Test creating a logger with an environment that has debug settings"""
    # Test for a module with debug enabled
    logger = DebugLogger.create_logger("link_card", mock_env)
    assert logger.enabled is True

    logger = DebugLogger.create_logger("gist_codeblock", mock_env)
    assert logger.enabled is True

    logger = DebugLogger.create_logger("x_twitter_card", mock_env)
    assert logger.enabled is True


@pytest.mark.debug
def test_get_debug_config_without_env() -> None:
    """Test getting debug configuration with no environment"""
    config = DebugLogger._get_debug_config()
    assert config == {}


@pytest.mark.debug
def test_get_debug_config_with_env(mock_env: MockMacrosPlugin) -> None:
    """Test getting debug configuration from a mock environment"""
    config = DebugLogger._get_debug_config(mock_env)
    assert config == {"link_card": True, "gist_codeblock": True, "x_twitter_card": True}


@pytest.mark.debug
def test_log_when_enabled(caplog: LogCaptureFixture) -> None:
    """Test logging when debug is enabled"""
    logger = DebugLogger("test_module", enabled=True)
    test_message = "Test debug message"
    test_data = {"key": "value"}

    logger.log(test_message, test_data)

    assert len(caplog.records) == 2
    assert test_message in caplog.records[0].message
    assert str(test_data) in caplog.records[1].message


@pytest.mark.debug
def test_log_when_disabled(caplog: LogCaptureFixture) -> None:
    """Test logging when debug is disabled"""
    logger = DebugLogger("test_module", enabled=False)
    test_message = "Test debug message"

    logger.log(test_message)

    assert len(caplog.records) == 0


@pytest.mark.debug
def test_log_with_string_data(caplog: LogCaptureFixture) -> None:
    """Test logging with a string data parameter"""
    logger = DebugLogger("test_module", enabled=True)
    test_message = "Test message"
    test_data = "String data"

    logger.log(test_message, test_data)

    assert len(caplog.records) == 2
    assert test_message in caplog.records[0].message
    assert test_data in caplog.records[1].message


@pytest.mark.debug
def test_create_logger_unknown_module(mock_env: MockMacrosPlugin) -> None:
    """Test creating a logger for an unknown module"""
    logger = DebugLogger.create_logger("unknown_module", mock_env)
    assert logger.enabled is False


@pytest.mark.debug
def test_logger_name_format() -> None:
    """Test the format of the logger name"""
    module_name = "test_module"
    logger = DebugLogger(module_name)
    assert logger.logger.name == f"mkdocs.plugins.macros-utils.{module_name}"

"""
Tests for MkDocs Macros Utils initialization module.
This module tests the functionality of the package's __init__.py,
including static file copying, file processing, and environment setup.
"""

import os
import logging
from pathlib import Path
import pytest
from _pytest.logging import LogCaptureFixture
from pytest import MonkeyPatch
from mkdocs.config import Config
from mkdocs.structure.files import File, Files
from mkdocs_macros_utils import (
    copy_static_files,
    on_files,
    define_env,
    MACROS_UTILS_DIR,
    MACROS_UTILS_CSS,
    MACROS_UTILS_JS,
)
from tests.python import MockMacrosPlugin


@pytest.fixture(autouse=True)
def setup_logging(caplog: LogCaptureFixture) -> None:
    """Setup logging for tests"""
    caplog.set_level(logging.INFO)


# -- Static File Tests ------------------------------
def test_copy_static_files(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    """Test copying of static files"""
    # Create mock plugin directory structure
    plugin_dir = tmp_path / "plugin"
    docs_dir = tmp_path / "docs"

    # Create necessary directories
    (plugin_dir / "static" / "css").mkdir(parents=True)
    (plugin_dir / "static" / "js").mkdir(parents=True)

    # Create mock static files
    for css_file in MACROS_UTILS_CSS:
        css_path = plugin_dir / "static" / "css" / css_file
        css_path.write_text("/* CSS content */")

    for js_file in MACROS_UTILS_JS:
        js_path = plugin_dir / "static" / "js" / js_file
        js_path.write_text("// JS content")

    # Test copying
    with caplog.at_level(logging.INFO):
        copy_static_files(plugin_dir, docs_dir)

    # Verify CSS files were copied
    css_dest = docs_dir / MACROS_UTILS_DIR
    for css_file in MACROS_UTILS_CSS:
        assert (css_dest / css_file).exists()

    # Verify JS files were copied
    js_dest = docs_dir / "javascripts" / "macros-utils"
    for js_file in MACROS_UTILS_JS:
        assert (js_dest / js_file).exists()

    # Test log messages
    assert any("Copied static CSS file" in record.message for record in caplog.records)
    assert any("Copied static JS file" in record.message for record in caplog.records)


def test_copy_static_files_update_only_newer(
    tmp_path: Path, caplog: LogCaptureFixture
) -> None:
    """Test that files are only copied when source is newer"""
    plugin_dir = tmp_path / "plugin"
    docs_dir = tmp_path / "docs"

    # Create necessary directories and initial files
    (plugin_dir / "static" / "css").mkdir(parents=True)
    css_dest = docs_dir / MACROS_UTILS_DIR
    css_dest.mkdir(parents=True)

    # Create a test CSS file
    test_css = "link-card.css"
    src_path = plugin_dir / "static" / "css" / test_css
    dest_path = css_dest / test_css

    # Create initial files
    src_path.write_text("/* CSS content */")
    dest_path.write_text("/* Old CSS content */")

    # Set destination file to be newer
    os.utime(dest_path, (2000000000, 2000000000))

    # Copy files
    with caplog.at_level(logging.INFO):
        copy_static_files(plugin_dir, docs_dir)

    # Verify file wasn't copied (no log message)
    assert not any(
        "Copied static CSS file" in record.message for record in caplog.records
    )


# -- File Processing Tests ------------------------------
def test_on_files() -> None:
    """Test file processing during build"""
    # Create mock files
    files = Files(
        [
            File(
                path="test.md", src_dir="docs", dest_dir="site", use_directory_urls=True
            ),
            File(
                path=f"{MACROS_UTILS_DIR}/style.css",
                src_dir="docs",
                dest_dir="site",
                use_directory_urls=True,
            ),
            File(
                path="other/file.md",
                src_dir="docs",
                dest_dir="site",
                use_directory_urls=True,
            ),
        ]
    )

    config = Config(schema=[])
    result = on_files(files, config)

    # Normalize paths to use forward slashes for consistent comparison
    paths = [f.src_path.replace("\\", "/") for f in result]
    expected_style_css = f"{MACROS_UTILS_DIR}/style.css".replace("\\", "/")

    # Verify files are processed correctly
    assert "test.md" in paths
    assert expected_style_css in paths
    assert "other/file.md" in paths


# -- Environment Setup Tests ------------------------------
def test_define_env_success(
    tmp_path: Path, caplog: LogCaptureFixture, monkeypatch: MonkeyPatch
) -> None:
    """Test successful environment setup"""
    mock_env = MockMacrosPlugin(conf={"docs_dir": str(tmp_path)})

    # Create necessary plugin directory structure
    plugin_dir = tmp_path / "plugin"
    (plugin_dir / "static" / "css").mkdir(parents=True)
    (plugin_dir / "static" / "js").mkdir(parents=True)

    # Create mock static files
    for css_file in MACROS_UTILS_CSS:
        (plugin_dir / "static" / "css" / css_file).write_text("/* CSS */")
    for js_file in MACROS_UTILS_JS:
        (plugin_dir / "static" / "js" / js_file).write_text("/* JS */")

    # Monkeypatch __file__ for plugin directory detection
    monkeypatch.setattr("mkdocs_macros_utils.__file__", str(plugin_dir / "__init__.py"))

    with caplog.at_level(logging.INFO):
        define_env(mock_env)

    assert any("successfully" in record.message for record in caplog.records)
    assert hasattr(mock_env, "link_card")
    assert hasattr(mock_env, "gist_codeblock")
    assert hasattr(mock_env, "x_twitter_card")


def test_define_env_failure(caplog: LogCaptureFixture) -> None:
    """Test environment setup failure handling"""
    mock_env = MockMacrosPlugin(conf={})  # Missing docs_dir

    with caplog.at_level(logging.ERROR):
        define_env(mock_env)

    assert any("Failed to initialize" in record.message for record in caplog.records)

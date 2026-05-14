"""
Zensical macros module for enhanced documentation components.
"""

from pathlib import Path
import shutil
import logging
import os
from typing import Any, Dict
from zensical.extensions.macros import MacroEnv

from . import link_card
from . import gist_codeblock
from . import x_twitter_card

logger = logging.getLogger("zensical.macros-utils")

MACROS_UTILS_DIR = "stylesheets/macros-utils"
MACROS_UTILS_CSS = ["link-card.css", "gist-cb.css", "x-twitter-link-card.css"]
MACROS_UTILS_JS = ["x-twitter-widget.js"]


def copy_static_files(plugin_dir: Path, docs_dir: Path) -> None:
    """
    静的ファイル（CSS、JS）を指定のディレクトリにコピーする

    Args:
        plugin_dir (Path): プラグインのディレクトリ
        docs_dir (Path): ドキュメントのディレクトリ
    """
    css_dest = docs_dir / MACROS_UTILS_DIR
    css_dest.mkdir(parents=True, exist_ok=True)

    js_dest = docs_dir / "javascripts" / "macros-utils"
    js_dest.mkdir(parents=True, exist_ok=True)

    for css_file in MACROS_UTILS_CSS:
        css_src = plugin_dir / "static" / "css" / css_file
        css_dest_path = css_dest / css_file
        if css_src.exists() and (
            not css_dest_path.exists()
            or os.path.getmtime(css_src) > os.path.getmtime(css_dest_path)
        ):
            shutil.copy2(css_src, css_dest_path)
            logger.info(f"Copied static CSS file: {css_file}")

    for js_file in MACROS_UTILS_JS:
        js_src = plugin_dir / "static" / "js" / js_file
        js_dest_path = js_dest / js_file
        if js_src.exists() and (
            not js_dest_path.exists()
            or os.path.getmtime(js_src) > os.path.getmtime(js_dest_path)
        ):
            shutil.copy2(js_src, js_dest_path)
            logger.info(f"Copied static JS file: {js_file}")


def _get_docs_dir() -> Path:
    """Return the docs directory path.

    Checks MACROS_UTILS_DOCS_DIR env var first, then defaults to 'docs' relative to CWD.
    """
    docs_dir_env = os.environ.get("MACROS_UTILS_DOCS_DIR", "docs")
    path = Path(docs_dir_env)
    if not path.is_absolute():
        path = Path(os.getcwd()) / path
    return path


def _load_config() -> Dict[str, Any]:
    """Load full config from mkdocs.yml or zensical config in CWD if available."""
    cwd = Path(os.getcwd())
    for config_name in ("mkdocs.yml", "mkdocs.yaml"):
        config_path = cwd / config_name
        if config_path.exists():
            try:
                import yaml  # type: ignore[import]

                with open(config_path) as f:
                    return dict(yaml.safe_load(f) or {})
            except Exception:
                pass
    return {}


def _load_extra_config() -> Dict[str, Any]:
    """Load extra settings from mkdocs.yml or zensical config in CWD if available."""
    return dict(_load_config().get("extra", {}))


def define_env(env: MacroEnv) -> None:
    """
    Zensicalマクロモジュールの環境を定義する
    """
    plugin_dir = Path(__file__).parent

    try:
        docs_dir = _get_docs_dir()

        # Make config values available to sub-modules via env.variables
        config = _load_config()
        extra = dict(config.get("extra", {}))
        if extra:
            env.variables["extra"] = extra
        site_url = str(config.get("site_url", ""))
        if site_url:
            env.variables["_site_url"] = site_url

        copy_static_files(plugin_dir, docs_dir)

        link_card.define_env(env)
        gist_codeblock.define_env(env)
        x_twitter_card.define_env(env)

        logger.info("Zensical macros utils initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize zensical macros utils: {e}")

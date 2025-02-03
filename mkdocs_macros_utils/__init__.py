"""
MkDocs Macros Cards plugin for enhanced documentation components.
"""

from pathlib import Path
import shutil
import logging
import os
from mkdocs.config import Config
from mkdocs.structure.files import Files
from mkdocs_macros.plugin import MacrosPlugin

from . import link_card

# from . import gist_codeblock
from . import gist_codeblock_async
from . import x_twitter_card

logger = logging.getLogger("mkdocs.plugins.macros-utils")

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


def on_files(files: Files, config: Config) -> Files:
    """
    ビルド時のファイル処理

    Args:
        files (Files): MkDocsファイルコレクション
        config (Config): MkDocs設定

    Returns:
        Files: 更新されたファイルコレクション
    """
    # macros-utilsディレクトリ内のファイルのみを有効にする
    allowed_files = [
        f for f in files if not str(f.src_path).startswith(MACROS_UTILS_DIR)
    ]
    allowed_files.extend(
        [
            f
            for f in files
            if str(f.src_path).startswith(os.path.join(MACROS_UTILS_DIR, ""))
        ]
    )
    return allowed_files


def define_env(env: MacrosPlugin) -> None:
    """
    MkDocsマクロプラグインの環境を定義する
    """
    # プラグインのディレクトリを取得
    plugin_dir = Path(__file__).parent

    try:
        # ドキュメントディレクトリを取得
        docs_dir = Path(env.conf["docs_dir"])

        # スタティックファイルをコピー
        copy_static_files(plugin_dir, docs_dir)

        # マクロを登録
        link_card.define_env(env)
        # gist_codeblock.define_env(env)
        gist_codeblock_async.define_env(env)
        x_twitter_card.define_env(env)

        logger.info("MkDocs Macros Utils initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize MkDocs Macros Utils: {e}")

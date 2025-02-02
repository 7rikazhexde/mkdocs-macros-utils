# mkdocs-macros-utils

MkDocs Macros provides macros to enhance cards, code blocks, etc. in MkDocs documents.

## Features

- **Link Card**: Create attractive link cards with images and descriptions
- **Gist Code Block**: Embed and syntax-highlight code from GitHub Gists
- **X/Twitter Card**: Embed tweets with proper styling and dark mode support

## Installation

Currently, the package can be installed from GitHub using Poetry:

1. Add the dependency to your project's `pyproject.toml`

    ```toml
    [project]
    dependencies = [
        "mkdocs-macros-utils@git+https://github.com/7rikazhexde/mkdocs-macros-utils.git@main"
    ]
    ```

    or

    ```bash
    poetry add "mkdocs-macros-utils@git+https://github.com/7rikazhexde/mkdocs-macros-utils.git@main"
    ```

    !!! info "I plan to make this package available via pip in the future."

    !!! tip "To reflect the latest code, remove mkdocs-macros-utils once and then add it again."

        ```bash
        poetry remove mkdocs-macros-utils
        poetry add "mkdocs-macros-utils@git+https://github.com/7rikazhexde/mkdocs-macros-utils.git#main"
        ```

1. Install using Poetry

    ```bash
    poetry install
    ```

## Usage

1. Add the plugin to your `mkdocs.yml`

    ```yaml
    plugins:
      - macros:
          modules: [mkdocs_macros_utils]

    markdown_extensions:
      - attr_list
      - md_in_html

    extra:
      debug:
        link_card: false  # Set to true for debug logging
        gist_codeblock: false
        x_twitter_card: false

    extra_css:
      - stylesheets/macros-utils/link-card.css
      - stylesheets/macros-utils/gist-cb.css
      - stylesheets/macros-utils/x-twitter-link-card.css

    extra_javascript:
      - javascripts/macros-utils/x-twitter-widget.js
    ```

1. Start the development server

    ```bash
    poetry run mkdocs serve
    ```

The plugin will automatically create the required directories and copy CSS/JS files during the build process.

## [Examples](./examples/index.md)

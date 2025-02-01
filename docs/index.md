# MkDocs Macros Cards

MkDocs Macros Cards is a plugin that provides enhanced card and code block functionality for MkDocs.

## Features

- **Link Card**: Create attractive link cards with images and descriptions
- **Gist Code Block**: Embed and syntax-highlight code from GitHub Gists
- **X/Twitter Card**: Embed tweets with proper styling and dark mode support

## Installation

```bash
cd your_mkdocs_project
git clone https://github.com/7rikazhexde/mkdocs-macros-utils.git
cd mkdocs-macros-utils
poetry install
```

## Usage

Add the plugin to your `mkdocs.yml`.

```yaml
plugins:
  - macros:
      modules: [mkdocs_macros_utils]

extra_css:
  - stylesheets/macros-utils/link-card.css
  - stylesheets/macros-utils/gist-cb.css
  - stylesheets/macros-utils/x-twitter-link-card.css

extra_javascript:
  - javascripts/macros-utils/x-twitter-widget.js
```

Run `poetry run mkdocs serve` under `your_project`.  
The necessary files(`.css/.js`) will be copied under docs before the build and the server will start.

```bash
cd ../
poetry run mkdocs serve
```

## [Examples](./examples/index.md)

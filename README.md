# mkdocs-macros-utils

MkDocs Macros provides macros to enhance cards, code blocks, etc. in MkDocs documents.

## Features

- Gist Code Block: Embed and syntax-highlight code from GitHub Gists
- Link Card: Create attractive link cards with images and descriptions
- X/Twitter Card: Embed tweets with proper styling and dark mode support

## Installation

```bash
cd your_mkdocs_project
git clone https://github.com/7rikazhexde/mkdocs-macros-utils.git
cd mkdocs-macros-utils
poetry install
cd ../
poetry run mkdocs serve
```

## Usage

Add the plugin to your `mkdocs.yml`

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

Run `poetry run mkdocs serve`.  
Files required before the build are copied under docs and the server is started.

## Documentation

For detailed usage and examples, please see the [documentation](docs/index.md).

## License

MIT License - see the [LICENSE](LICENSE) file for details.

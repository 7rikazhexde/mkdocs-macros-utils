---
title: Link Card Macro
tags:
  - MkDocs Macros
  - Custom Component
  - Link Card
  - Material for Mkdocs
description: Documentation showing a macro for creating custom link card macros using the MkDocs Macros Plugin
---

# Link Card Macro

## Summary

This section describes a macro to display custom link cards in Mkdocs.

!!! info "This macro is assumed to be used with [Material for Mkdocs](https://squidfunk.github.io/mkdocs-material/)."

## Usage

Custom link cards can be added by including a macro in markdown with the following parameters

Macro name: `link_card`.

| Parameters | Required | Default | Description |
|-----------|------|------------|------|
| `url` | required | None | Linked URL |
| `title` | required | None | Card Title |
| `description` | optional | blank text | card description |
| `image_path` | optional | default image | image to display on card |
| `domain` | optional | Default domain of the site | Domain Display |
| `external` | optional | False | external link flag |
| `svg_path` | optional | Automatic determination from URL | Custom SVG icon path in format "user_id/gist_id/filename" (e.g., "7rikazhexde/d418315080179e7c1bd9a7a4366b81f6/github-cutom-icon.svg") |

### Exapmples

Create a link card based on the css settings and the values specified in the parameters.

#### Examples of minimum parameters

??? tip "How to specify minimum parameters"

    !!! info

        If `image_path` is omitted, `assets/img/site.png` will be displayed.

    ```markdown
    {% raw %}
    {{ link_card(
        url="Linked path (absolute path)",
        title="page title",
    ) }}
    {% endraw %}
    ```

    ```markdown
    {% raw %}
    {{ link_card(
        url="https://7rikazhexde.github.io/mkdocs-macros-utils/",
        title="MkDocs Macros Utils Documentation",
    ) }}
    {% endraw %}
    ```

{{ link_card(
    url="https://7rikazhexde.github.io/mkdocs-macros-utils/",
    title="MkDocs Macros Utils Documentation",
) }}

#### Examples of maximum parameters

??? tip "How to specify maximum parameters"

    !!! info

        If `image_path` and `svg_path` are specified, `svg_path` takes precedence.

    ```markdown
    {% raw %}
    {{ link_card(
        url="https://7rikazhexde-pkm-obsidian-mkdocs.netlify.app/ja/development/tools/design/inkscape/",
        title="Inkscape - 7rikazhexde PKM",
        description="Inkscape tips",
        external=True,
        image_path="examples/images/inkscape.png"
        svg_path=""
    ) }}
    {% endraw %}
    ```  

##### Specify image_path

{{ link_card(
    url="https://7rikazhexde.github.io/mkdocs-macros-utils/",
    title="Inkscape - 7rikazhexde PKM",
    description="Inkscape tips",
    external=True,
    image_path="examples/images/inkscape.png"
) }}

##### Specify svg_path

{{ link_card(
    url="https://7rikazhexde.github.io/mkdocs-macros-utils/",
    title="Inkscape - 7rikazhexde PKM",
    description="Inkscape tips",
    external=True,
    image_path="examples/images/inkscape.png",
    svg_path="7rikazhexde/b57ab5c007c8fc5229b3b0aee72af702/simple-materialformkdocs.svg"
) }}

#### Example of GitHub repository link

For links to GitHub repositories, the GitHub icon is automatically displayed by default.
If you want to display a custom SVG icon, specify the Gist path in the `svg_path` parameter.

??? tip "How to specify a GitHub repository"

    ```markdown
    {% raw %}
    {{ link_card(
        url="GitHub repository URL",
        title="Page title",
        description="Repository description",
        external=True
    ) }}
    {% endraw %}
    ```

    ```markdown
    {% raw %}
    {{ link_card(
        url="https://github.com/pyenv-win/pyenv-win/blob/master/docs/installation.md#git-commands",
        title="pyenv-win Installation Guide",
        description="Git installation commands for pyenv-win",
        external=True
    ) }}  
    {% endraw %}
    ```

{{ link_card(
    url="https://github.com/pyenv-win/pyenv-win/blob/master/docs/installation.md#git-commands",
    title="pyenv-win Installation Guide",
    description="Git installation commands for pyenv-win",
    external=True
) }}

#### Example of `svg_path` link

??? tip "How to designate SVG as the icon for card links"

    !!! tip "About the SVG file to be used"

        - Create a gist in the following format (public release) and specify the `GistID` and `filename.svg` in the `link_card` parameter: `svg_path`.
        - In case of specific colors (fill="#333" (gray),fill="black" (black)), replace with class="custom-link-card-icon" considering light mode and dark mode display, and change colors by CSS targeting class="custom-link-card-icon".
        - To ensure consistent color transitions between light and dark modes, this code removes `fill-rule="evenodd"` and `clip-rule="evenodd"` attributes during SVG processing. If you need these styling effects, please consider using alternative SVG approaches.
        - lists of SVG data published by the author can be found [here](./svg-info.md).

        ```css
        {% raw %}<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
            <path fill="#2088ff" d="M26.666 0C11.97 0 0 11.97 0 26.666c0 12.87 9.181 23.651 21.334 26.13v37.87c0 11.77 9.68 21.334 21.332 21.334h.195c1.302 9.023 9.1 16 18.473 16C71.612 128 80 119.612 80 109.334s-8.388-18.668-18.666-18.668c-9.372 0-17.17 6.977-18.473 16h-.195c-8.737 0-16-7.152-16-16V63.779a18.514 18.514 0 0 0 13.24 5.555h2.955c1.303 9.023 9.1 16 18.473 16 9.372 0 17.169-6.977 18.47-16h11.057c1.303 9.023 9.1 16 18.473 16 10.278 0 18.666-8.39 18.666-18.668C128 56.388 119.612 48 109.334 48c-9.373 0-17.171 6.977-18.473 16H79.805c-1.301-9.023-9.098-16-18.471-16s-17.171 6.977-18.473 16h-2.955c-6.433 0-11.793-4.589-12.988-10.672 14.58-.136 26.416-12.05 26.416-26.662C53.334 11.97 41.362 0 26.666 0zm0 5.334A21.292 21.292 0 0 1 48 26.666 21.294 21.294 0 0 1 26.666 48 21.292 21.292 0 0 1 5.334 26.666 21.29 21.29 0 0 1 26.666 5.334zm-5.215 7.541C18.67 12.889 16 15.123 16 18.166v17.043c0 4.043 4.709 6.663 8.145 4.533l13.634-8.455c3.257-2.02 3.274-7.002.032-9.045l-13.635-8.59a5.024 5.024 0 0 0-2.725-.777zm-.117 5.291 13.635 8.588-13.635 8.455V18.166zm40 35.168a13.29 13.29 0 0 1 13.332 13.332A13.293 13.293 0 0 1 61.334 80 13.294 13.294 0 0 1 48 66.666a13.293 13.293 0 0 1 13.334-13.332zm48 0a13.29 13.29 0 0 1 13.332 13.332A13.293 13.293 0 0 1 109.334 80 13.294 13.294 0 0 1 96 66.666a13.293 13.293 0 0 1 13.334-13.332zm-42.568 6.951a2.667 2.667 0 0 0-1.887.78l-6.3 6.294-2.093-2.084a2.667 2.667 0 0 0-3.771.006 2.667 2.667 0 0 0 .008 3.772l3.974 3.96a2.667 2.667 0 0 0 3.766-.001l8.185-8.174a2.667 2.667 0 0 0 .002-3.772 2.667 2.667 0 0 0-1.884-.78zm48 0a2.667 2.667 0 0 0-1.887.78l-6.3 6.294-2.093-2.084a2.667 2.667 0 0 0-3.771.006 2.667 2.667 0 0 0 .008 3.772l3.974 3.96a2.667 2.667 0 0 0 3.766-.001l8.185-8.174a2.667 2.667 0 0 0 .002-3.772 2.667 2.667 0 0 0-1.884-.78zM61.334 96a13.293 13.293 0 0 1 13.332 13.334 13.29 13.29 0 0 1-13.332 13.332A13.293 13.293 0 0 1 48 109.334 13.294 13.294 0 0 1 61.334 96zM56 105.334c-2.193 0-4 1.807-4 4 0 2.195 1.808 4 4 4s4-1.805 4-4c0-2.193-1.807-4-4-4zm10.666 0c-2.193 0-4 1.807-4 4 0 2.195 1.808 4 4 4s4-1.805 4-4c0-2.193-1.807-4-4-4zM56 108c.75 0 1.334.585 1.334 1.334 0 .753-.583 1.332-1.334 1.332-.75 0-1.334-.58-1.334-1.332 0-.75.585-1.334 1.334-1.334zm10.666 0c.75 0 1.334.585 1.334 1.334 0 .753-.583 1.332-1.334 1.332-.75 0-1.332-.58-1.332-1.332 0-.75.583-1.334 1.332-1.334z"/><path fill="#79b8ff" d="M109.334 90.666c-9.383 0-17.188 6.993-18.477 16.031a2.667 2.667 0 0 0-.265-.011l-2.7.09a2.667 2.667 0 0 0-2.578 2.751 2.667 2.667 0 0 0 2.752 2.578l2.7-.087a2.667 2.667 0 0 0 .097-.006C92.17 121.029 99.965 128 109.334 128c10.278 0 18.666-8.388 18.666-18.666s-8.388-18.668-18.666-18.668zm0 5.334a13.293 13.293 0 0 1 13.332 13.334 13.29 13.29 0 0 1-13.332 13.332A13.293 13.293 0 0 1 96 109.334 13.294 13.294 0 0 1 109.334 96z"/>
        </svg>{% endraw %}
        ```

    ```markdown
    {% raw %}
    {{ link_card(
        url="GitHub repository URL",
        title="Page title",
        description="Repository description",
        external=True,
        svg_path="UserID/GistID/sample.svg"
    ) }}
    {% endraw %}
    ```

    ```markdown
    {% raw %}
    {{ link_card(
        url="https://github.com/marketplace/actions/json-to-variables-setter",
        title="JSON to Variables Setter",
        description="GitHub Action designed to parse a JSON file and set the resulting variables (such as operating systems, programming language versions, and GitHub Pages branch) as outputs in a GitHub Actions workflow.",
        external=True,
        svg_path="7rikazhexde/996eec6799c869324bf9fe2e93b1a876/github-actions-icon.svg"
    ) }}
    {% endraw %}
    ```

{{ link_card(
    url="https://github.com/marketplace/actions/json-to-variables-setter",
    title="JSON to Variables Setter",
    description="GitHub Action designed to parse a JSON file and set the resulting variables (such as operating systems, programming language versions, and GitHub Pages branch) as outputs in a GitHub Actions workflow.",
    external=True,
    svg_path="7rikazhexde/996eec6799c869324bf9fe2e93b1a876/github-actions-icon.svg"
) }}

#### Example of a Hatena blog post

If the link is to a Hatena Blog post, the Hatena Blog logo will automatically be displayed.

??? tip "How to specify a Hatena blog post"

    ```markdown
    {% raw %}
    {{ link_card(
        url="Hatena blog post URL",
        title="Page title",
        description="Article description",
        domain="username.hatenablog.com",
        external=True
    ) }}
    {% endraw %}
    ```

    ```markdown
    {% raw %}
    {{ link_card(
        url="https://7rikazhexde-techlog.hatenablog.com/entry/2023/07/08/173536#Pyenv%E3%81%AB%E3%82%88%E3%82%8BPython%E7%92%B0%E5%A2%83%E3%82%92%E6%A7%8B%E7%AF%89%E3%81%99%E3%82%8B",
        title="Building a Python environment on Ubuntu on RaspberryPi using Pyenv and Poetry",
        description="Explanation of how to build a Python environment using Pyenv and Poetry on Ubuntu on RaspberryPi.",
        external=True
    ) }}  
    {% endraw %}
    ```

{{ link_card(
    url="https://7rikazhexde-techlog.hatenablog.com/entry/2023/07/08/173536#Pyenv%E3%81%AB%E3%82%88%E3%82%8BPython%E7%92%B0%E5%A2%83%E3%82%92%E6%A7%8B%E7%AF%89%E3%81%99%E3%82%8B",
    title="Building a Python environment on Ubuntu on RaspberryPi using Pyenv and Poetry",
    description="Explanation of how to build a Python environment using Pyenv and Poetry on Ubuntu on RaspberryPi.",
    external=True
) }}

#### Other Web site examples

For websites other than those listed above, icons are not displayed on card links by default.

??? tip "How to specify other Web sites"

    ```markdown
    {% raw %}
    {{ link_card(
        url="URL of the site",
        title="page title",
        description="page description",
        external=True
    ) }}
    {% endraw %}
    ```

    ```markdown
    {% raw %}  
    {{ link_card(
        url="https://news.mynavi.jp/techplus/article/zeropython-122/",
        title="Introduction to Python from scratch",
        description="A series of courses explaining the basics of Python programming",
        external=True
    ) }}
    {% endraw %}
    ```

{{ link_card(
    url="https://news.mynavi.jp/techplus/article/zeropython-122/",
    title="Introduction to Python from scratch",
    description="A series of courses explaining the basics of Python programming",
    external=True
) }}

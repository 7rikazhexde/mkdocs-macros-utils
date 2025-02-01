---
title: MkDocs Custom X-Twitter Link Card Macro
tags:
 - MkDocs Macros
 - Custom Component
 - Link Card
 - X(Twitter)
description: Documentation showing a macro to display X (formerly Twitter) link cards using the MkDocs Macros Plugin.
---

# Macros to display X (formerly Twitter) link cards using MkDocs Macros Plugin

## Summary

This page describes a macro to display X (formerly Twitter) link cards using MkDocs.

## Usage

You can add X (formerly Twitter) link cards by specifying the following parameters in your markdown file.

Macro name: `x_twitter_card`.

| Parameters | Required | Description |
|-----------|------|------|
| `url` | required | URL of X (former Twitter) |

### Examples

!!! info "How to use `x_twitter_card`"

    ```markdown
    {% raw %}
    {{ x_twitter_card('https://x.com/tw_7rikazhexde/status/1882447777269170238') }}
    {% endraw %}
    ```

{{ x_twitter_card('https://x.com/tw_7rikazhexde/status/1882447777269170238') }}

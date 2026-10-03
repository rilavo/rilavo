---
title: Documentation Site Technology (MkDocs Material)
status: Accepted
date: 2024-02-20
deciders: [Rilavo Core Team]
consulted: [Documentation Team, DevRel]
informed: [All Contributors]
---

# ADR-006: Documentation Site Technology (MkDocs Material)

## Context and Problem Statement

Rilavo needs a documentation site that supports:
- Multi-language API reference (Python, TypeScript, Go, Next.js, WordPress)
- Interactive playground with live credential verification
- Versioned documentation
- Excellent search and navigation
- Easy contribution workflow (Markdown)
- Custom styling and components
- CI/CD integration

## Decision Drivers

- Multi-language API reference generation (mkdocstrings)
- Markdown-based authoring for easy contributions
- Interactive JavaScript components (playground)
- Versioned documentation support
- Excellent search (built-in or Algolia)
- Responsive design
- CI/CD integration (GitHub Pages, Netlify)
- Customizable theme and components

## Considered Options

### Option 1: Docusaurus (React-based)

Popular React-based documentation framework.

**Pros:**
- Large community, many plugins
- React-based customization
- Good versioning support
- Algolia DocSearch integration

**Cons:**
- Requires React/JavaScript expertise
- Heavier build process
- API reference generation less mature for non-JS languages
- Python/Go API reference requires custom plugins

### Option 2: MkDocs Material (Chosen)

MkDocs with Material theme and mkdocstrings for API reference.

**Pros:**
- Python-based (matches Rilavo's Python SDK)
- mkdocstrings supports Python, TypeScript, Go, and more
- Material theme is polished and accessible
- Excellent search (built-in minisearch or Algolia)
- Markdown authoring with extensions (pymdownx)
- Custom components via overrides
- Lightweight build, fast CI
- GitHub Pages deployment built-in
- Custom JavaScript/CSS via overrides

**Cons:**
- Less React ecosystem for interactive components
- mkdocstrings Go/TypeScript handlers less mature than Python
- Custom interactive components require vanilla JS

### Option 3: Sphinx + Read the Docs

Traditional Python documentation toolchain.

**Pros:**
- Mature, battle-tested
- Excellent for Python API reference
- Read the Docs hosting free for open source

**Cons:**
- Poor support for non-Python languages
- reStructuredText less popular than Markdown
- Less modern UI
- Limited interactive component support

## Decision Outcome

Chosen option: **Option 2: MkDocs Material with mkdocstrings** because it provides the best balance of multi-language API reference generation, Markdown authoring, customization, and CI/CD integration.

### Positive Consequences

- Python API reference auto-generated from docstrings (mkdocstrings Python handler)
- TypeScript/Go API reference via mkdocstrings handlers or manual pages
- Interactive playground via custom JavaScript in overrides
- Fast builds (~2 seconds)
- Easy GitHub Pages deployment
- Markdown authoring lowers contribution barrier

### Negative Consequences

- Go/TypeScript mkdocstrings handlers less mature
- Custom interactive components require vanilla JS (no React)
- Versioning requires manual configuration

## Implementation Plan

1. MkDocs Material with custom theme overrides
2. mkdocstrings for Python API reference (auto-generated)
3. Manual API reference pages for TypeScript, Go, Next.js, WordPress
4. Custom JavaScript for interactive playground
5. Custom CSS for Rilavo branding
6. GitHub Actions for build and deploy to GitHub Pages
7. Versioned documentation with mike

## Links

- [docs-site/mkdocs.yml](/docs-site/mkdocs.yml)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

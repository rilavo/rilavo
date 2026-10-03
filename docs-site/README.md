# Rilavo Documentation Site

This directory contains the MkDocs-Material configuration for the Rilavo documentation website.

## Structure

```
docs-site/
├── mkdocs.yml                 # Main configuration
├── requirements-docs.txt      # Python dependencies
├── docs/                      # Markdown content (organized by section)
│   ├── index.md               # Landing page
│   ├── getting-started/       # Tutorials T1-T4 + playground
│   ├── protocol/              # Protocol specification (Waves 1-2, 6)
│   ├── sdks/                  # SDK guides + parity matrix
│   ├── commercial/            # Product features (Waves 3, 5)
│   ├── operations/            # Operations, deployment, survival
│   ├── api/                   # Auto-generated API reference (gitignored)
│   └── playground/            # Interactive credential playground
├── overrides/                 # Material theme overrides
│   ├── stylesheets/extra.css  # Custom styles
│   └── scripts/playground.js  # Interactive playground logic
├── scripts/                   # API reference generators
│   ├── gen_python_api.py
│   ├── gen_ts_api.py
│   ├── gen_go_api.py
│   └── gen_all_api.py
└── .github/workflows/
    └── docs.yml               # GitHub Pages deployment
```

## Local Development

```bash
# Install dependencies
pip install -r requirements-docs.txt

# Generate API references (requires source repos)
python scripts/gen_all_api.py

# Serve locally with live reload
mkdocs serve

# Build for production
mkdocs build --strict
```

## Deployment

The site is automatically deployed to GitHub Pages on push to `main` via `.github/workflows/docs.yml`.

## Adding Content

1. **New tutorial**: Add to `docs/getting-started/` and update `mkdocs.yml` nav
2. **New protocol spec**: Add to `docs/protocol/` and update nav
3. **New SDK**: Add to `docs/sdks/<name>/` and update nav
4. **API changes**: Re-run `python scripts/gen_all_api.py`

## Theme Customization

- Colors: Edit `theme.palette` in `mkdocs.yml`
- Styles: Edit `overrides/stylesheets/extra.css`
- Scripts: Edit `overrides/scripts/playground.js`
- Templates: Add `.html` files to `overrides/`

## Interactive Playground

The playground (`docs/playground/index.md`) runs entirely client-side using the Web Crypto API. No backend required.

Features:
- Generate Ed25519 keypairs (issuer + agent)
- Issue credentials with customizable fields
- Verify credentials (signature, expiry, audience, revocation)
- Create and verify Proof-of-Possession requests

## Versioning

Use [mike](https://github.com/jimporter/mike) for versioned documentation:

```bash
# Deploy version
mike deploy 0.1.0 latest --push --config-file=mkdocs.yml

# List versions
mike list --config-file=mkdocs.yml

# Set default
mike set-default latest --config-file=mkdocs.yml
```

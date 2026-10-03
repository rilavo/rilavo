#!/usr/bin/env bash
# Rilavo WordPress Quick-Start Bootstrap
# Usage: bash <(curl -sSL https://rilavo.dev/bootstrap/wordpress) --audience verifier:myapp.com

set -euo pipefail

AUDIENCE=""
PLUGIN_DIR="rilavo-verification"

usage() {
    echo "Usage: $0 [--audience AUDIENCE] [--dir DIR]"
    echo "  --audience Verifier audience (required)"
    echo "  --dir      Plugin directory name (default: rilavo-verification)"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --audience) AUDIENCE="$2"; shift 2 ;;
        --dir) PLUGIN_DIR="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ -z "$AUDIENCE" ]]; then
    echo "Error: --audience is required"
    usage
fi

echo "🚀 Creating Rilavo WordPress plugin: $PLUGIN_DIR"
echo "   Audience: $AUDIENCE"

# Create plugin directory
mkdir -p "$PLUGIN_DIR"
cd "$PLUGIN_DIR"

# Generate scaffold
if command -v rilavo &> /dev/null; then
    rilavo init --framework wordpress --dir .
else
    echo "Installing rilavo CLI..."
    pip install rilavo
    rilavo init --framework wordpress --dir .
fi

# Update audience
sed -i "s|YOUR_AUDIENCE_HERE|$AUDIENCE|g" rilavo-verification.php
if [[ -f .env.example ]]; then
    cp .env.example .env
    sed -i "s|YOUR_AUDIENCE_HERE|$AUDIENCE|g" .env
fi

# Install composer dependencies
composer install --no-dev

echo ""
echo "✅ WordPress plugin created successfully!"
echo ""
echo "Next steps:"
echo "  cd $PLUGIN_DIR"
echo "  # Edit .env with your issuer key"
echo "  # Zip and upload to WordPress: zip -r rilavo-verification.zip ."
echo "  # Activate in WordPress admin > Plugins"
echo ""
echo "📚 Documentation: https://docs.rilavo.org"

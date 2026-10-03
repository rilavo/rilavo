#!/usr/bin/env bash
# Rilavo Next.js Quick-Start Bootstrap
# Usage: npx create-rilavo-app my-app --template=nextjs --audience verifier:myapp.com

set -euo pipefail

AUDIENCE=""
PROJECT_NAME="my-rilavo-app"
PACKAGE_MANAGER="npm"

usage() {
    echo "Usage: $0 [--audience AUDIENCE] [--project-name NAME] [--pm PM]"
    echo "  --audience     Verifier audience (required)"
    echo "  --project-name Project name (default: my-rilavo-app)"
    echo "  --pm           Package manager: npm, yarn, pnpm (default: npm)"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --audience) AUDIENCE="$2"; shift 2 ;;
        --project-name) PROJECT_NAME="$2"; shift 2 ;;
        --pm) PACKAGE_MANAGER="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ -z "$AUDIENCE" ]]; then
    echo "Error: --audience is required"
    usage
fi

echo "🚀 Creating Rilavo Next.js project: $PROJECT_NAME"
echo "   Audience: $AUDIENCE"

# Use npx to create the app
npx create-rilavo-app "$PROJECT_NAME" --template nextjs --audience "$AUDIENCE" --pm "$PACKAGE_MANAGER"

echo ""
echo "✅ Next.js project created successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  # Edit .env with your issuer key"
echo "  $PACKAGE_MANAGER install"
echo "  $PACKAGE_MANAGER run dev"
echo ""
echo "📚 Documentation: https://docs.rilavo.org"
echo "🔧 Interactive API: http://localhost:3000/docs (when running)"

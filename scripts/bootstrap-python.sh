#!/usr/bin/env bash
# Rilavo Python Quick-Start Bootstrap
# Usage: curl -sSL https://rilavo.dev/bootstrap/python | bash -s -- --audience verifier:myapp.com

set -euo pipefail

AUDIENCE=""
PROJECT_NAME="my-rilavo-app"
FRAMEWORK="fastapi"

usage() {
    echo "Usage: $0 [--audience AUDIENCE] [--project-name NAME] [--framework FRAMEWORK]"
    echo "  --audience     Verifier audience (required)"
    echo "  --project-name Project name (default: my-rilavo-app)"
    echo "  --framework    Framework: fastapi, express, nextjs, go, wordpress"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --audience) AUDIENCE="$2"; shift 2 ;;
        --project-name) PROJECT_NAME="$2"; shift 2 ;;
        --framework) FRAMEWORK="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ -z "$AUDIENCE" ]]; then
    echo "Error: --audience is required"
    usage
done

echo "🚀 Bootstrapping Rilavo $FRAMEWORK project: $PROJECT_NAME"
echo "   Audience: $AUDIENCE"

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Generate scaffold using rilavo CLI
if command -v rilavo &> /dev/null; then
    rilavo init --framework "$FRAMEWORK" --project-name "$PROJECT_NAME" --dir .
else
    echo "Installing rilavo..."
    pip install rilavo
    rilavo init --framework "$FRAMEWORK" --project-name "$PROJECT_NAME" --dir .
fi

# Create .env from example
if [[ -f .env.example ]]; then
    cp .env.example .env
    # Update audience
    sed -i "s|YOUR_AUDIENCE_HERE|$AUDIENCE|g" .env
    echo "✅ Updated .env with audience: $AUDIENCE"
fi

echo ""
echo "✅ Project created successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  # Edit .env with your issuer key"
echo "  # Install dependencies and run:"
if [[ "$FRAMEWORK" == "fastapi" ]]; then
    echo "  pip install -e ."
    echo "  uvicorn main:app --reload"
elif [[ "$FRAMEWORK" == "express" ]]; then
    echo "  npm install"
    echo "  npm run dev"
elif [[ "$FRAMEWORK" == "nextjs" ]]; then
    echo "  npm install"
    echo "  npm run dev"
elif [[ "$FRAMEWORK" == "go" ]]; then
    echo "  go mod tidy"
    echo "  go run ."
elif [[ "$FRAMEWORK" == "wordpress" ]]; then
    echo "  composer install"
    echo "  # Activate plugin in WordPress admin"
fi
echo ""
echo "📚 Documentation: https://docs.rilavo.org"
echo "🔧 Interactive API: http://localhost:8000/docs (when running)"

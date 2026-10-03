#!/usr/bin/env bash
# Rilavo Go Quick-Start Bootstrap
# Usage: go install github.com/rilavo/rilavo-go/cmd/rilavo-bootstrap@latest && rilavo-bootstrap my-service --audience verifier:myapp.com

set -euo pipefail

AUDIENCE=""
PROJECT_NAME="my-rilavo-service"
MODULE_PATH=""

usage() {
    echo "Usage: $0 [--audience AUDIENCE] [--project-name NAME] [--module MODULE]"
    echo "  --audience     Verifier audience (required)"
    echo "  --project-name Project name (default: my-rilavo-service)"
    echo "  --module       Go module path (e.g., github.com/user/project)"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --audience) AUDIENCE="$2"; shift 2 ;;
        --project-name) PROJECT_NAME="$2"; shift 2 ;;
        --module) MODULE_PATH="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ -z "$AUDIENCE" ]]; then
    echo "Error: --audience is required"
    usage
fi

if [[ -z "$MODULE_PATH" ]]; then
    MODULE_PATH="github.com/user/$PROJECT_NAME"
fi

echo "🚀 Creating Rilavo Go service: $PROJECT_NAME"
echo "   Audience: $AUDIENCE"
echo "   Module: $MODULE_PATH"

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Initialize Go module
go mod init "$MODULE_PATH"

# Get Rilavo SDK
go get github.com/rilavo/rilavo-go@latest

# Generate scaffold
if command -v rilavo &> /dev/null; then
    rilavo init --framework go --project-name "$PROJECT_NAME" --dir .
else
    echo "Installing rilavo CLI..."
    go install github.com/rilavo/rilavo-protocol/cmd/rilavo@latest
    rilavo init --framework go --project-name "$PROJECT_NAME" --dir .
fi

# Update go.mod with correct module path
sed -i "s|module YOUR_MODULE_NAME|module $MODULE_PATH|" go.mod

# Update audience in main.go and .env
sed -i "s|YOUR_AUDIENCE_HERE|$AUDIENCE|g" main.go
if [[ -f .env.example ]]; then
    cp .env.example .env
    sed -i "s|YOUR_AUDIENCE_HERE|$AUDIENCE|g" .env
fi

# Tidy dependencies
go mod tidy

echo ""
echo "✅ Go service created successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  # Edit .env with your issuer key"
echo "  go run ."
echo ""
echo "📚 Documentation: https://docs.rilavo.org"
echo "🔧 Interactive API: http://localhost:8080/docs (when running)"

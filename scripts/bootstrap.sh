#!/usr/bin/env bash
# Rilavo Universal Bootstrap
# Usage: curl -sSL https://rilavo.dev/bootstrap | bash -s -- --sdk python --audience verifier:myapp.com

set -euo pipefail

SDK="python"
AUDIENCE=""
PROJECT_NAME="my-rilavo-app"
FRAMEWORK=""
MODULE_PATH=""
PLUGIN_DIR="rilavo-verification"

usage() {
    cat <<EOF
Rilavo Universal Bootstrap

Usage: $0 [options]

Options:
  --sdk SDK           SDK to bootstrap: python, node, go, nextjs, express, wordpress (default: python)
  --audience AUDIENCE Verifier audience identifier (required)
  --project-name NAME Project name (default: my-rilavo-app)
  --framework FW      Framework for python/node: fastapi, express, nextjs, go, wordpress
  --module PATH       Go module path (e.g., github.com/user/project)
  --dir DIR           WordPress plugin directory name (default: rilavo-verification)
  -h, --help          Show this help

Examples:
  # Python FastAPI
  curl -sSL https://rilavo.dev/bootstrap | bash -s -- --sdk python --audience verifier:api.example.com

  # Next.js
  curl -sSL https://rilavo.dev/bootstrap | bash -s -- --sdk nextjs --audience verifier:api.example.com

  # Go service
  curl -sSL https://rilavo.dev/bootstrap | bash -s -- --sdk go --audience verifier:api.example.com --module github.com/user/my-service

  # WordPress plugin
  curl -sSL https://rilavo.dev/bootstrap | bash -s -- --sdk wordpress --audience verifier:api.example.com --dir my-plugin
EOF
    exit 1
}

SDK="python"
AUDIENCE=""
PROJECT_NAME="my-rilavo-app"
FRAMEWORK=""
MODULE_PATH=""
PLUGIN_DIR="rilavo-verification"

while [[ $# -gt 0 ]]; do
    case $1 in
        --sdk) SDK="$2"; shift 2 ;;
        --audience) AUDIENCE="$2"; shift 2 ;;
        --project-name) PROJECT_NAME="$2"; shift 2 ;;
        --framework) FRAMEWORK="$2"; shift 2 ;;
        --module) MODULE_PATH="$2"; shift 2 ;;
        --dir) PLUGIN_DIR="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ -z "$AUDIENCE" ]]; then
    echo "Error: --audience is required"
    usage
fi

# Set default framework based on SDK
if [[ -z "$FRAMEWORK" ]]; then
    case $SDK in
        python) FRAMEWORK="fastapi" ;;
        node) FRAMEWORK="express" ;;
        nextjs) FRAMEWORK="nextjs" ;;
        go) FRAMEWORK="go" ;;
        wordpress) FRAMEWORK="wordpress" ;;
        *) echo "Unknown SDK: $SDK"; usage ;;
    esac
fi

# Validate framework for SDK
case $SDK in
    python)
        [[ "$FRAMEWORK" =~ ^(fastapi|express|nextjs)$ ]] || { echo "Invalid framework for python: $FRAMEWORK"; usage; }
        ;;
    node)
        [[ "$FRAMEWORK" =~ ^(express|nextjs)$ ]] || { echo "Invalid framework for node: $FRAMEWORK"; usage; }
        ;;
    nextjs)
        FRAMEWORK="nextjs"
        ;;
    go)
        FRAMEWORK="go"
        ;;
    wordpress)
        FRAMEWORK="wordpress"
        ;;
    *)
        echo "Unknown SDK: $SDK"
        usage
        ;;
esac

echo "🚀 Bootstrapping Rilavo $FRAMEWORK project: $PROJECT_NAME"
echo "   Audience: $AUDIENCE"

# Dispatch to SDK-specific bootstrap
case $SDK in
    python)
        exec bash <(curl -sSL https://rilavo.dev/bootstrap/python) --audience "$AUDIENCE" --project-name "$PROJECT_NAME" --framework "$FRAMEWORK"
        ;;
    node)
        exec bash <(curl -sSL https://rilavo.dev/bootstrap/node) --audience "$AUDIENCE" --project-name "$PROJECT_NAME" --framework "$FRAMEWORK"
        ;;
    nextjs)
        exec bash <(curl -sSL https://rilavo.dev/bootstrap/nextjs) --audience "$AUDIENCE" --project-name "$PROJECT_NAME" --pm npm
        ;;
    go)
        MODULE_ARG=""
        [[ -n "$MODULE_PATH" ]] && MODULE_ARG="--module $MODULE_PATH"
        exec bash <(curl -sSL https://rilavo.dev/bootstrap/go) --audience "$AUDIENCE" --project-name "$PROJECT_NAME" $MODULE_ARG
        ;;
    wordpress)
        PLUGIN_DIR_ARG=""
        [[ -n "$PLUGIN_DIR" ]] && PLUGIN_DIR_ARG="--dir $PLUGIN_DIR"
        exec bash <(curl -sSL https://rilavo.dev/bootstrap/wordpress) --audience "$AUDIENCE" $PLUGIN_DIR_ARG
        ;;
    *)
        echo "Unknown SDK: $SDK"
        usage
        ;;
esac

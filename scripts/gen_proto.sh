#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=src/prompt_autoimprove/api/grpc/generated
mkdir -p "$OUT"
touch "$OUT/__init__.py"

uv run python -m grpc_tools.protoc \
  -I proto \
  --python_out="$OUT" \
  --pyi_out="$OUT" \
  --grpc_python_out="$OUT" \
  proto/autoimprove/v1/autoimprove.proto

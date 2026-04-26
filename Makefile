.PHONY: install lint fmt typecheck test run-http run-grpc proto hooks

install:
	uv sync --all-groups

lint:
	uv run ruff check .

fmt:
	uv run ruff format .

typecheck:
	uv run ty check src

test:
	uv run pytest -q

run-http:
	uv run uvicorn prompt_autoimprove.api.http.app:app --reload --port 8000

run-grpc:
	uv run python -m prompt_autoimprove.api.grpc.server

proto:
	./scripts/gen_proto.sh

hooks:
	uv run prek install --hook-type pre-commit --hook-type commit-msg

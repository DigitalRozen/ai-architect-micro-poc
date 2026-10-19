.PHONY: help sync lint fmt test

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

sync: ## Install dev dependencies
	uv sync

lint: ## Lint and check formatting
	uv run ruff check .
	uv run ruff format --check .

fmt: ## Auto-format
	uv run ruff check --fix .
	uv run ruff format .

test: ## Run unit tests
	uv run pytest -q

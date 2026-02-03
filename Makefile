# HiMaLAYAS Publication Makefile

.PHONY: help format lint test build publish clean

format: ## Format Python files using Black
	black --line-length=100 .

clean: ## Remove build artifacts and caches
	find . \( \
		-name ".DS_Store" -o \
		-name ".ipynb_checkpoints" -o \
		-name "__pycache__" \
	\) -exec rm -rf {} \;

help: ## Show available make targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS = ":.*##"}; {printf "%-12s %s\n", $$1, $$2}'

poetry run black .
poetry run yapf --in-place --recursive .
poetry run ruff check --fix
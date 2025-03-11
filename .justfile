default:
    just --list

tests:
    poetry run pytest --cov --cov-fail-under=100

type_check:
    poetry run mypy src/ tests/

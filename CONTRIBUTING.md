
# Contributing

## Setup
```bash
pip install -e ".[dev,cli,app]"
pre-commit install
```

## Running tests
```bash
pytest -q
```

## Pull requests
- Create feature branches from `main`.
- Ensure CI is green (lint, types, tests).
- Describe changes clearly and update docs if needed.

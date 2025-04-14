# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands
- Backend testing: `cd backend && pytest` or `cd backend && make test`
- Run a single test: `cd backend && pytest tests/test_models.py::test_placeholder`
- Quality checks: `cd backend && make quality`
- Install requirements: `cd backend && make requirements`
- Compile requirements: `cd backend && make compile-requirements`

## Code Style Guidelines
- Python: Follow PEP 8 with max line length of 120
- Use isort for import sorting
- Document classes and functions with docstrings
- Type hints are encouraged but not required
- Error handling should use appropriate exceptions with descriptive messages
- Use pytest for testing, with descriptive test function names
- Frontend uses React and follows standard JSX conventions

Always run `make quality` before creating a PR to ensure consistent code style.

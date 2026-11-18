# Contributing to AeroFamily

Thank you for contributing to AeroFamily! We welcome contributions to improve our smog protection platform, respiratory health algorithms, and community monitoring tools.

## Architecture Guidelines

- **Service Layer**: Pure business logic resides in `services/`. All algorithms (CADR, inhalation dosage, diurnal curve modeling) must be pure functions or well-tested classes.
- **Routing**: API endpoints reside in `routers/` using FastAPI `APIRouter`. Each domain possesses its own router module.
- **Data Models**: Use Pydantic schemas in `models/schemas.py` and strict domain enumerations in `models/enums.py`.
- **Error Handling**: Use custom typed exceptions from `core/exceptions.py`. Avoid generic `HTTPException` in service logic.
- **Configuration**: Application configuration is centralized in `core/config.py` using `pydantic-settings`.

## Coding Standards

- Follow PEP 8 style guidelines.
- Provide type hints for all function arguments and return types.
- Document modules, classes, and public functions using Google-style docstrings.
- Ensure all monetary amounts are denominated in Indian Rupees (`₹`).

## Running Tests

Before submitting any pull request, ensure all tests pass:

```bash
python run_tests.py
```

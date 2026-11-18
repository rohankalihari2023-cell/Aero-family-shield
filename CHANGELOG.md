# Changelog

All notable changes to AeroFamily are documented in this file.

## [2.1.0] - 2026-11-18

### Added
- Modular FastAPI `APIRouter` structure in `routers/` separating system, atmospheric, advisor, routine, IAQ, impact, and community domains.
- Type-safe domain enumerations (`MaskType`, `CommuteMode`, `HomeSealing`, `CookingFuel`, `HousingType`, `HumidifierWaterType`, `AirQualityCategory`, `IncidentSeverity`).
- Service contracts and protocol abstractions in `core/interfaces.py` enforcing Dependency Inversion.
- Automated GitHub Actions continuous integration pipeline in `.github/workflows/ci.yml`.
- Unit test suites covering router mounting and interface protocol conformance (63 automated tests).
- Developer contribution guidelines in `CONTRIBUTING.md`.

### Changed
- Refactored `server.py` to use application factory pattern (`create_app`) with global domain exception handling.
- Converted currency calculations to Indian Rupees (`₹`) across IAQ and impact modules.
- Upgraded documentation with comprehensive Google-style docstrings and explicit type hints.

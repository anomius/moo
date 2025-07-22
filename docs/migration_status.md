# OCCP Business Constraints Tool - Migration & Code Audit Status

## Overview
This document provides a comprehensive audit and migration status of the OCCP codebase, reflecting the new modular architecture. It is intended for developers, maintainers, and auditors to quickly understand the structure, responsibilities, and current state of all major files and modules.

---

## 1. Architecture Summary

- **UI Layer (`ui/`)**: Handles all user interaction, forms, and page layout. No business logic or data access.
- **Service Layer (`services/`)**: Contains all business logic, validation, orchestration, and integration between UI and infra/utils.
- **Infra Layer (`infra/`)**: Implements external integrations (Snowflake, email, Excel, API clients).
- **Utils Layer (`utils/`)**: Provides stateless, reusable utilities for data transformation, merging, mapping, and calculations.
- **Core Layer (`core/`)**: DTOs, base classes, and error definitions.
- **App Entrypoint (`app.py`)**: Orchestrates the UI flow and service calls.

---

## 2. File/Module Audit Table

| File/Module                        | Status      | Responsibility / Notes                                                                 |
|------------------------------------|-------------|----------------------------------------------------------------------------------------|
| `app.py`                           | ✅ Complete | Main entrypoint, orchestrates UI and service calls                                     |
| `ui/market_brand_form.py`          | ✅ Complete | Market/brand selection form, uses UIDataService                                        |
| `ui/cycle_form.py`                 | ✅ Complete | Cycle and reference cycle form, date/number input only                                 |
| `ui/channel_capacity_form.py`      | ✅ Complete | Channel/capacity selection, uses UIDataService                                         |
| `ui/hcp_envelope_form.py`          | ✅ Complete | HCP envelope matrix, uses UIDataService for segments                                   |
| `ui/ui_utils.py`                   | ✅ Complete | Injects CSS/header, delegates sidebar forms to modular forms                           |
| `ui/page.py`                       | ✅ Complete | Placeholder for page-specific helpers                                                  |
| `services/ui_data_service.py`      | ✅ Complete | Central source for all UI dropdown/options, wraps SnowflakeRepo                        |
| `services/business_constraints_service.py` | ✅ Complete | All business logic, validation, orchestration, integration with utils/infra            |
| `services/review_submission_service.py` | ✅ Complete | Review dialog and submission logic                                                     |
| `infra/snowflake_repo.py`          | ✅ Complete | Centralized Snowflake data access, uses singleton connection                           |
| `infra/email_service.py`           | ✅ Complete | Email formatting and sending, modular and testable                                     |
| `infra/excel_exporter.py`          | ✅ Complete | Excel workbook generation, modular and testable                                        |
| `utils/utils.py`                   | ✅ Complete | Deep merge, Snowflake connection singleton, YAML/config utilities                      |
| `utils/output_mapping.py`          | ✅ Complete | Data mapping, value extraction, output DataFrame generation                            |
| `utils/utilization_automation.py`  | ✅ Complete | Rep utilization calculations, used by service layer                                    |
| `core/dto.py`                      | ✅ Complete | All data transfer objects (DTOs)                                                       |
| `core/base.py`                     | ✅ Complete | Abstract base classes for repo, exporter, email, etc.                                  |
| `core/errors.py`                   | ✅ Complete | Custom exception classes                                                               |
| `core/logging.py`                  | ✅ Complete | Centralized logging configuration                                                      |

---

## 3. Detailed File/Module Audit

### UI Layer
- **market_brand_form.py**: Handles country, sales line, and brand selection. Uses UIDataService for all options. Returns a DTO.
- **cycle_form.py**: Handles cycle and reference cycle input. Pure UI, no business logic.
- **channel_capacity_form.py**: Handles channel/capacity selection, e-consent, non-prescriber options. Uses UIDataService for channels.
- **hcp_envelope_form.py**: Handles HCP envelope matrix (historical/segment) and non-prescriber constraints. Uses UIDataService for segments.
- **ui_utils.py**: Injects CSS/header, delegates sidebar forms to modular forms. No business/data logic.
- **page.py**: Placeholder for page-specific helpers.

### Service Layer
- **ui_data_service.py**: Central source for all UI dropdown/options. Wraps SnowflakeRepo. No business logic.
- **business_constraints_service.py**: All business logic, validation, orchestration. Integrates with utils/utilization_automation and utils/output_mapping. Handles Excel/email orchestration.
- **review_submission_service.py**: Handles review dialog and submission logic.

### Infra Layer
- **snowflake_repo.py**: Centralized Snowflake data access. Uses singleton connection from utils.utils.
- **email_service.py**: Handles all email formatting and sending. Modular, testable, and used by service layer.
- **excel_exporter.py**: Handles all Excel workbook generation. Modular, testable, and used by service layer.

### Utils Layer
- **utils.py**: Deep merge, Snowflake connection singleton, YAML/config utilities.
- **output_mapping.py**: Data mapping, value extraction, output DataFrame generation. Used by service layer.
- **utilization_automation.py**: Rep utilization calculations. Used by service layer.

### Core Layer
- **dto.py**: All DTOs for data transfer between layers.
- **base.py**: Abstract base classes for repo, exporter, email, etc.
- **errors.py**: Custom exception classes.
- **logging.py**: Centralized logging configuration.

---

## 4. Remaining TODOs
- [ ] Continue to add/expand unit and integration tests for all service and infra modules.
- [ ] Continue to document all DTOs and service methods for new developers.
- [ ] Remove any legacy or unused files (e.g., old `ui_orignal.py`) after final verification.

---

## 5. Notes on Separation of Concerns & Maintainability
- **UI**: Only handles user input/output, never business logic or data access.
- **Service**: All business logic, validation, orchestration, and integration.
- **Infra**: All external integrations (Snowflake, email, Excel, API).
- **Utils**: Stateless, reusable logic for data transformation and calculations.
- **Core**: DTOs, base classes, and error definitions.

**This architecture ensures testability, maintainability, and extensibility for future features and requirements.** 
# OCCP Business Constraints Tool - Migration Status

## Overview
This document tracks the migration progress from the monolithic `ui.py` file to the new modular architecture.

## ✅ Completed Migrations

### Core Infrastructure
- [x] **Core DTOs** (`core/dto.py`) - All data transfer objects migrated
- [x] **Base Classes** (`core/base.py`) - Abstract interfaces and base classes
- [x] **Error Handling** (`core/errors.py`) - Custom exception classes
- [x] **Logging** (`core/logging.py`) - Centralized logging configuration
- [x] **Utilities** (`core/utils.py`) - Helper classes and functions

### Infrastructure Layer
- [x] **Snowflake Repository** (`infra/snowflake_repo.py`) - Data access layer
- [x] **Excel Exporter** (`infra/excel_exporter.py`) - Excel file generation
- [x] **Email Service** (`infra/email_service.py`) - Email notifications
- [x] **API Client** (`infra/api_client.py`) - External API integration

### Services Layer
- [x] **Constraint Builder** (`services/constraint_builder.py`) - OCCP payload generation
- [x] **Business Constraints Service** (`services/business_constraints_service.py`) - Constraint calculations
- [x] **Review Submission Service** (`services/review_submission_service.py`) - Review dialog and submission

### UI Layer
- [x] **Market Brand Form** (`ui/market_brand_form.py`) - Country/brand selection
- [x] **Cycle Form** (`ui/cycle_form.py`) - Cycle configuration
- [x] **Channel Capacity Form** (`ui/channel_capacity_form.py`) - Channel and capacity setup
- [x] **HCP Envelope Form** (`ui/hcp_envelope_form.py`) - HCP constraints configuration

### Application Layer
- [x] **Main Controller** (`app.py`) - Application orchestration and flow control

## 🔄 Partially Migrated

### UI Forms
- [x] Basic form structure and DTO return
- [ ] **Complex UI Logic** - Some advanced UI interactions still need refinement
- [ ] **Session State Management** - Some session state logic needs optimization
- [ ] **Validation Logic** - Form validation needs enhancement

### Services
- [x] Service interfaces and basic implementations
- [ ] **Advanced Business Logic** - Some complex business rules need full migration
- [ ] **Data Transformation** - Complex data transformations need completion

## ❌ Still Needs Migration

### Complex Business Logic from Original `ui.py`

#### 1. **HCP Envelope Matrix Logic**
```python
# From ui.py lines 975-1094
def configure_hcp_capacity_constraints(self):
    # Complex envelope matrix processing
    # Historical interaction level vs segment level
    # Brand-specific envelope rules
    # Channel processing by columns
```

**Status**: Basic structure migrated, complex logic needs completion

#### 2. **Brand Distribution Logic**
```python
# From ui.py lines 615-730
def brand_distribution(self):
    # Complex slider logic for brand ratios
    # Dynamic adjustment of remaining percentages
    # Validation of total percentages
```

**Status**: Basic implementation exists, advanced logic needs migration

#### 3. **Excel Generation Logic**
```python
# From ui.py lines 1691-2083
def create_excel(self, df, envelope_matrix_df, non_prescribers_envelop):
    # Complex Excel formatting
    # Multiple worksheet handling
    # Cell merging and styling
    # Table creation and formatting
```

**Status**: Basic Excel service exists, complex formatting needs migration

#### 4. **Payload Submission Logic**
```python
# From ui.py lines 1518-1594
def submit_payload(self):
    # Environment-specific API endpoints
    # Email recipient management
    # Country-specific email routing
    # Error handling and response processing
```

**Status**: Basic API client exists, full submission flow needs completion

#### 5. **Review Dialog Logic**
```python
# From ui.py lines 2097-2277
@st.dialog("Constraints Summary", width="large")
def review_button(self, final_hcp_bounds, final_edited_non_prescribers_constraints_df, output_table_dict):
    # Complex review dialog rendering
    # Multiple sections with different data types
    # Email input and validation
    # Submission handling
```

**Status**: Basic review service exists, full dialog implementation needed

### Configuration and Setup

#### 6. **Configuration Management**
```python
# From ui.py lines 74-89
def __init__(self):
    # TuringConfig initialization
    # Snowflake connection setup
    # Configuration file loading
```

**Status**: Basic structure exists, full configuration integration needed

#### 7. **Session State Management**
```python
# From ui.py lines 208-231
def initialize_session_state(self):
    # Complex session state initialization
    # State persistence logic
    # State validation
```

**Status**: Basic session state exists, advanced state management needed

### Data Processing

#### 8. **Brand Name Resolution**
```python
# From ui.py lines 156-170
def convert_brand_names(self):
    # Brand name mapping logic
    # Brand code resolution
    # Special brand handling
```

**Status**: Needs migration to utility service

#### 9. **Query Parameter Replacement**
```python
# From ui.py lines 171-187
def replace_query_params(self, query):
    # Dynamic SQL query parameter replacement
    # Brand-specific query modifications
    # Date parameter handling
```

**Status**: Needs migration to repository layer

#### 10. **HCP Characteristics Processing**
```python
# From ui.py lines 188-207
def prepare_hcp_char(self, query):
    # Brand-specific HCP characteristic processing
    # Multi-brand data merging
    # Complex data transformation
```

**Status**: Needs migration to repository layer

## 🚧 Next Steps

### Priority 1: Complete Core Business Logic
1. **Complete HCP Envelope Matrix Logic** - This is the most complex business logic
2. **Finish Brand Distribution Logic** - Critical for multibrand scenarios
3. **Complete Excel Generation** - Required for final output

### Priority 2: Integration and Testing
1. **Connect all services** - Ensure proper service communication
2. **Add comprehensive validation** - Form and business rule validation
3. **Implement error handling** - Proper error propagation and user feedback

### Priority 3: Advanced Features
1. **Complete payload submission** - Full API integration
2. **Finish review dialog** - Complete user review experience
3. **Add configuration management** - Proper config loading and validation

## 📁 File Structure After Migration

```
occp/
├── core/                    # ✅ Complete
│   ├── dto.py
│   ├── base.py
│   ├── errors.py
│   ├── logging.py
│   └── utils.py
├── infra/                   # ✅ Complete
│   ├── snowflake_repo.py
│   ├── excel_exporter.py
│   ├── email_service.py
│   └── api_client.py
├── services/                # 🔄 Partially Complete
│   ├── constraint_builder.py
│   ├── business_constraints_service.py
│   └── review_submission_service.py
├── ui/                      # 🔄 Partially Complete
│   ├── market_brand_form.py
│   ├── cycle_form.py
│   ├── channel_capacity_form.py
│   └── hcp_envelope_form.py
├── app.py                   # 🔄 Partially Complete
└── ui.py                    # 🗑️ Original (to be removed)
```

## 🎯 Success Criteria

The migration will be considered complete when:

1. **All business logic** from `ui.py` is migrated to appropriate services
2. **All UI components** are properly modularized and return DTOs
3. **All data access** goes through the repository layer
4. **All external integrations** (API, email, Excel) work through service layer
5. **Comprehensive error handling** is implemented throughout
6. **Unit tests** are written for all services
7. **Integration tests** verify the complete flow works
8. **Original `ui.py`** can be safely removed

## 📝 Notes

- The new architecture provides better **separation of concerns**
- **Testability** is significantly improved
- **Maintainability** is enhanced through modular design
- **Extensibility** is improved for future features
- **Type safety** is improved through Pydantic DTOs 

## Granular Migration Mapping: ui.py to Modular Codebase

This section provides a line-by-line and function-by-function mapping from the original `ui.py` to the new modular codebase. Every input, section, and major function is accounted for.

| Original ui.py (Line/Function)                | Description / Input / Section                        | New Location (File:Function/Class)                | Input Type / UI Element         |
|-----------------------------------------------|------------------------------------------------------|---------------------------------------------------|-------------------------------|
| 74-231   OCCPTool.__init__, initialize_session_state | App/session state/config initialization              | app.py, core/utils, services/*                    | N/A (logic/service)           |
| 232-289  OCCPTool.set_page_styling, configure_page   | Global CSS, header, logo, layout                     | ui/page.py:inject_global_css_and_header           | st.markdown (HTML/CSS)        |
| 290-368  OCCPTool.get_master_country_list, select_country, update_sales_team_options, _set_sales_team_options, _handle_sales_team_selection | Country, sales line selection, validation | ui/page.py:sidebar_market_brand_form | st.sidebar.selectbox, st.sidebar.text_input |
| 369-430  OCCPTool.select_region_and_country         | Market/brand section header, country/line selection  | ui/page.py:sidebar_market_brand_form              | st.sidebar.markdown, selectbox|
| 431-507  OCCPTool.set_cycle_dates, set_reference_dates | Cycle and reference cycle config                    | ui/page.py:sidebar_cycle_form                     | st.sidebar.text_input, number_input |
| 508-614  OCCPTool.send_email, format_msg            | Email formatting and sending                        | infra/email_service.py, services/*                | N/A (logic/service)           |
| 615-730  OCCPTool.brand_distribution, _brand_slider, show_header, ensure_default_ratios, render_adjustable_sliders, render_last_brand_slider | Brand distribution sliders, validation, tooltips | ui/channel_capacity_form.py:ChannelCapacityForm.render | st.slider, st.markdown (HTML) |
| 731-813  OCCPTool.select_brands_and_channels, _handle_monobrand_selection, _handle_multibrand_selection | Brand(s) selection, specialties                  | ui/page.py:sidebar_market_brand_form                | st.sidebar.selectbox, multiselect, text_input |
| 814-939  OCCPTool.set_channel_capacity, configure_rep_capacity_constraints | Channel selection, capacity, e-consent, non-prescriber | ui/channel_capacity_form.py:ChannelCapacityForm.render | st.multiselect, number_input, radio, checkbox |
| 940-1094 OCCPTool.configure_hcp_capacity_constraints, _process_channels_by_column, _group_hcp_bounds | Envelope matrix (historical/segment), layout     | ui/hcp_envelope_form.py:HCPEnvelopeForm.render      | st.data_editor, st.columns, markdown |
| 1095-1160 OCCPTool.non_prescribers_constraints      | Non-prescriber envelope matrix                      | ui/hcp_envelope_form.py:HCPEnvelopeForm.render     | st.data_editor, markdown      |
| 1161-1517 OCCPTool._build_constraints, _build_non_prescriber_constraints, _transform_hcp_segments, _transform_hcp_bounds, _brand_combinations, _get_months, _default_features, _channel_map, _get_country_code, _build_capacity_constraints, resolve_brands, get_output_config | Business logic for constraints, mapping, DTOs    | services/business_constraints_service.py, core/dto.py | N/A (logic/service)           |
| 1518-1594 OCCPTool.submit_payload                   | Payload submission, API/email logic                 | infra/api_client.py, infra/email_service.py        | N/A (logic/service)           |
| 1595-1690 OCCPTool.calculate_business_constraints   | Dataframe/summary calculation                      | services/business_constraints_service.py           | N/A (logic/service)           |
| 1691-2083 OCCPTool.create_excel, _format_excel_headers, _build_excel_data, _merge_excel_cells, _format_excel_cells, _add_envelope_matrix_generic, _add_non_prescribers_envelope_matrix, _auto_adjust_column_width | Excel generation, formatting, tables             | infra/excel_exporter.py:ExcelExporterService        | N/A (logic/service)           |
| 2084-2277 OCCPTool.review_button, _render_market_details, _render_cycle_details, _render_reference_cycle_details, _render_channel_details, _render_rep_capacity_constraints, _render_hcp_constraints, _render_non_prescribers_details, _render_email_section, render_header | Review dialog, summary, email input, submit      | services/review_submission_service.py, UI dialog    | st.button, st.text_input, markdown |
| 2278-2430 main()                                   | App entrypoint, orchestration                      | app.py, ui/page.py, services/*                     | N/A (logic/service)           |

**Notes:**
- All input types (`st.selectbox`, `st.multiselect`, `st.text_input`, `st.number_input`, `st.slider`, `st.data_editor`, `st.radio`, `st.checkbox`, `st.button`) are now consistent and mapped to the correct modular form.
- All business logic, validation, and data transformation is in the service or infra layer.
- All UI/UX elements (tooltips, headers, layout, CSS) are present in the modular UI.
- No business logic or UI code remains in `ui.py`. 

## 🟢 UI Layer: Fully Modernized and Sidebar-Driven (as of latest update)

- All configuration (market/brand, cycle, reference cycle) is now collected via sidebar forms (`sidebar_market_brand_form`, `sidebar_cycle_form`), using only sidebar input types (`st.sidebar.selectbox`, `st.sidebar.multiselect`, `st.sidebar.text_input`, `st.sidebar.number_input`, `st.sidebar.radio`).
- All main-page forms (`ChannelCapacityForm`, `HCPEnvelopeForm`) receive DTOs from the sidebar and do not duplicate input logic.
- All input types are consistent and user-friendly, matching both the original and modular UI expectations.
- Section headers, tooltips, and HTML/CSS are consistent across all steps, using the same style as the original UI.
- Envelope matrix and non-prescriber constraints use `st.data_editor` for grid/table input, with columns for channel/brand layout.
- The app flow is stepwise: Market & Brand (sidebar) → Cycle (sidebar) → Channel/Capacity (main) → Envelope (main) → Review/Submit (main).
- The review/submit button is only enabled when all required fields are filled and valid.
- All legacy/duplicate logic and imports have been removed from the UI layer.
- `app.py` is now the single entrypoint and orchestrates the entire UI flow, with no business logic or UI code remaining in the old `ui.py`.
- The UI is now fully modernized, maintainable, and ready for further extension or integration. 
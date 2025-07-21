import pytest
import streamlit as st
from ui.channel_capacity_form import ChannelCapacityForm
from ui.hcp_envelope_form import HCPEnvelopeForm
from ui.page import sidebar_market_brand_form, sidebar_cycle_form

@pytest.fixture(autouse=True)
def clear_session(monkeypatch):
    # Clear Streamlit session state before each test
    st.session_state.clear()

# --- ChannelCapacityForm ---
def test_channel_capacity_form_returns_dto(monkeypatch):
    monkeypatch.setattr(st, "multiselect", lambda *a, **k: ["F2F", "Remote"])
    monkeypatch.setattr(st, "radio", lambda *a, **k: "No")
    monkeypatch.setattr(st, "number_input", lambda *a, **k: 5.0)
    monkeypatch.setattr(st, "checkbox", lambda *a, **k: True)
    monkeypatch.setattr(st, "slider", lambda *a, **k: 50)
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: "Low")
    brands = ["BrandA", "BrandB"]
    mode = "Multibrand"
    dto, brand_dist = ChannelCapacityForm.render(brands, mode)
    assert dto is not None
    assert set(dto.channels) == {"F2F", "Remote"}
    assert dto.daily_capacity["F2F"] == 5.0
    assert brand_dist is not None

# --- HCPEnvelopeForm ---
def test_hcp_envelope_form_returns_dto(monkeypatch):
    # Simulate radio and data_editor for historical
    monkeypatch.setattr(st, "radio", lambda *a, **k: "Historical Interaction level")
    class DummyDF:
        def iterrows(self):
            return iter([(0, {"Reference Cycle Actual": 0, "Min": 1, "Max": 2})])
    monkeypatch.setattr(st, "data_editor", lambda *a, **k: DummyDF())
    channels = ["F2F"]
    brands = ["BrandA"]
    mode = "Monobrand"
    use_segment_matrix = False
    hist, seg, np = HCPEnvelopeForm.render(channels, brands, mode, use_segment_matrix)
    assert hist is not None
    assert seg is None

# --- sidebar_market_brand_form ---
def test_sidebar_market_brand_form(monkeypatch):
    monkeypatch.setattr(st.sidebar, "selectbox", lambda *a, **k: "Italy")
    monkeypatch.setattr(st.sidebar, "radio", lambda *a, **k: "Monobrand")
    monkeypatch.setattr(st.sidebar, "text_input", lambda *a, **k: "Specialty")
    monkeypatch.setattr(st.sidebar, "multiselect", lambda *a, **k: ["BrandA"])
    form = sidebar_market_brand_form()
    assert form is not None
    assert form.country == "Italy"

# --- sidebar_cycle_form ---
def test_sidebar_cycle_form(monkeypatch):
    monkeypatch.setattr(st.sidebar, "text_input", lambda *a, **k: "2024/01")
    monkeypatch.setattr(st.sidebar, "number_input", lambda *a, **k: 1)
    monkeypatch.setattr(st.sidebar, "markdown", lambda *a, **k: None)
    form = sidebar_cycle_form()
    assert form is not None 
"""Main application controller for the OCCP Business Constraints Tool."""

import os
import streamlit as st
from core.dto import DTOBundle
from ui.page import inject_global_css_and_header, sidebar_market_brand_form, sidebar_cycle_form
from ui.channel_capacity_form import ChannelCapacityForm
from ui.hcp_envelope_form import HCPEnvelopeForm
from services.business_constraints_service import BusinessConstraintsService

# Inject global CSS and header
inject_global_css_and_header(logo_path="./utils/turing_logo.PNG")

# Step 1: Market & Brand (sidebar)
market = sidebar_market_brand_form()
if market:
    # Step 2: Cycle & Reference Cycle (sidebar)
    cycle, reference = sidebar_cycle_form()
    if cycle and reference:
        # Step 3: Channel & Capacity (main page)
        st.markdown("## Step 3: Channel & Capacity Configuration")
        capacity, brand_distribution = ChannelCapacityForm.render(market.brand_names, market.mode)
        if capacity:
            # Step 4: Envelope Matrix (main page)
            st.markdown("## Step 4: HCP Envelope Configuration")
            historical_envelopes, segment_envelopes, non_prescriber_envelopes = HCPEnvelopeForm.render(
                capacity.channels, market.brand_names, market.mode, False
            )
            # Step 5: Review & Submit (main page)
            st.markdown("## Step 5: Review & Submit")
            # Validate all required fields
            required_fields = [
                market.country,
                market.brands,
                market.sales_line,
                cycle.name,
                cycle.start,
                cycle.working_days,
                reference.working_days,
                capacity.channels,
            ]
            all_channels_have_capacity = all(capacity.daily_capacity.get(ch, 0.0) > 0 for ch in capacity.channels)
            if all(required_fields) and all_channels_have_capacity:
                bundle = DTOBundle(
                    market=market,
                    cycle=cycle,
                    reference=reference,
                    distribution=brand_distribution,
                    capacity=capacity,
                    envelopes_hist=historical_envelopes,
                    envelopes_seg=segment_envelopes,
                    non_prescriber=non_prescriber_envelopes
                )
                # Show Veeva format section and review/submit button
                st.markdown(
                    """
                    <div class="tooltip">
                        <h5>Veeva Align Format:</h5>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                veeva_checkbox_value = st.radio(
                    "Do you require the OCCP output in Veeva Align format for review by Sales Representative?",
                    ("No", "Yes"),
                    horizontal=True,
                )
                st.session_state.veeva_checkbox = (veeva_checkbox_value == "Yes")
                st.markdown(
                    """
                    <style>
                    .custom-list {
                        color: #7a00e6;
                        font-size: 16px;
                    }
                    .custom-list ul {
                        display: flex;
                        list-style-type: disc;
                        padding-left: 0;
                    }
                    .custom-list ul li {
                        margin-right: 20px;
                    }
                    </style>
                    <div class="custom-list">
                        <h5>For OCCP calculation, we follow Customer Facing Guidance for effort allocation as:</h5>
                        <ul>
                            <li>Segment A: 40-50%</li>
                            <li>Segment B: 20-30%</li>
                            <li>Segment C: 10-15%</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                review = st.button("Review and Submit")
                if review:
                    st.success("Review and submission functionality will be implemented here!")
            else:
                st.warning("Please fill all required fields and ensure all channels have capacity values > 0.")
        else:
            st.warning("Please complete the channel and capacity configuration.")
    else:
        st.warning("Please complete the cycle configuration.")
else:
    st.warning("Please complete the market and brand selection.") 
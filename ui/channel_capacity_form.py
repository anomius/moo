"""Channel and capacity selection form."""

import streamlit as st
from typing import List, Optional
from core.base import PageForm
from core.dto import ChannelCapacityDTO, BrandDistributionDTO
from ui.ui_utils import inject_global_css_and_header
from services.ui_data_service import UIDataService

class ChannelCapacityForm(PageForm):
    """Form for channel and capacity selection."""
    
    @staticmethod
    def render(brands: List[str], mode: str) -> tuple[ChannelCapacityDTO, Optional[BrandDistributionDTO]]:
        inject_global_css_and_header(logo_path="./utils/turing_logo.PNG")
        st.markdown(
            """
            <div class="tooltip">
                <h5>Channel Constraints for Upcoming Cycle:</h5>
                <span class="tooltiptext">Choose the channels for the upcoming Omni Channel Call Plan (OCCP) cycle for the selected brand. Options include channels such as Remote and Face to Face.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        channels = UIDataService.get_channels()
        monobrand_channel = st.multiselect(
            "Select the OCCP channels in scope",
            channels,
            help="Choose the channels for upcoming OCCP Cycle for Monobrand OCCP interactions.",
        )
        multibrand_channel = []
        if mode == "Multibrand" and len(brands) >= 2:
            multibrand_channel = st.multiselect(
                "Select which Channel(s) can be Multibrand interactions?",
                monobrand_channel,
                help="Choose the channels for the upcoming Omni Channel Call Plan (OCCP) cycle for Multibrand interactions.",
            )
        is_any_rte_present = any(
            _channel in monobrand_channel or _channel in multibrand_channel
            for _channel in ["RTE-Open", "RTE-Sent"]
        )
        is_both_rte_present = all(
            _channel in monobrand_channel or _channel in multibrand_channel
            for _channel in ["RTE-Open", "RTE-Sent"]
        )
        e_consent_rte = True
        if is_both_rte_present:
            st.error("Please select either RTE-Open or RTE-Sent")
        if is_any_rte_present:
            e_consent_rte = st.checkbox(
                "E-consent Required for Rep Triggered Email (RTE)", value=True
            )
        brand_distribution = None
        if mode == "Multibrand" and len(brands) > 1:
            st.markdown(
                """
                <div class="tooltip">
                    <h5>Brand Distribution:</h5>
                    <span class="tooltiptext">
                        What percentage of the upcoming Omni Channel Call Plan (OCCP)
                        should be allocated for each selected brand.
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            ratios = {}
            remaining = 100
            for i, brand in enumerate(brands):
                if i == len(brands) - 1:
                    ratios[brand] = remaining
                    st.slider(
                        f"What percentage of the OCCP should be allocated to {brand}?",
                        1,
                        100,
                        remaining,
                        key=f"brand_ratio_{brand}",
                        step=1,
                        disabled=True,
                        help="Choose the brand distribution (in %) for multibrand OCCP interactions",
                    )
                else:
                    val = st.slider(
                        f"What percentage of the OCCP should be allocated to {brand}?",
                        1,
                        remaining,
                        remaining // (len(brands) - i),
                        key=f"brand_ratio_{brand}",
                        step=1,
                        help="Choose the brand distribution (in %) for multibrand OCCP interactions",
                    )
                    ratios[brand] = val
                    remaining -= val
            from services.business_constraints_service import BusinessConstraintsService
            try:
                BusinessConstraintsService.validate_brand_distribution(ratios)
                brand_distribution = BrandDistributionDTO(ratios=ratios)
            except ValueError as e:
                st.error(str(e))
                return None, None
        is_non_prescriber = st.radio(
            "Is Non-prescriber included in the Target list?",
            ("No", "Yes"),
            horizontal=True,
        )
        non_prescriber_priority = None
        if is_non_prescriber == "Yes":
            st.info(
                "**Note:** All non-prescribers and prescribers need to be identified by the country when sharing the target universe in the HCP-Rep mapping file."
            )
            non_prescriber_priority = st.selectbox(
                "Select the level of Non-Prescribers priority",
                ["Low", "Medium", "High"],
            )
        st.markdown(
            """
            <div class="tooltip">
                <h5>Rep Capacity Constraints for Upcoming Cycle:</h5>
                <span class="tooltiptext">Enter the average number of interactions a REP has per day for the channel. For example, a REP can have the capacity to hold one face to face meeting with health care professional per day on average, and about 5 remote meetings</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        daily_capacity = {}
        unique_channels = list(dict.fromkeys(monobrand_channel + multibrand_channel))
        for channel in unique_channels:
            label = (
                f"Avg interactions per REP per day for {channel} (Prescriber and Non-Prescribers Combined)"
                if is_non_prescriber == "Yes"
                else f"Avg interactions per REP per day for {channel}"
            )
            help_text = f"Enter the average number of interactions a REP has per day for the {channel}."
            daily_capacity[channel] = st.number_input(
                label=label,
                min_value=0.0,
                value=0.0,
                step=0.1,
                format="%.1f",
                key=f"channel_capacity_{channel}",
                help=help_text,
            )
        from services.business_constraints_service import BusinessConstraintsService
        try:
            BusinessConstraintsService.validate_channel_capacity(daily_capacity)
        except ValueError as e:
            st.error(str(e))
            return None, None
        st.session_state.monobrand_channel = monobrand_channel
        st.session_state.multibrand_channel = multibrand_channel
        st.session_state.e_consent_rte = e_consent_rte
        st.session_state.is_non_prescriber = is_non_prescriber
        st.session_state.non_prescriber_priority = non_prescriber_priority
        st.session_state.daily_capacity = daily_capacity
        st.session_state.unique_channels = unique_channels
        capacity_dto = ChannelCapacityDTO(
            channels=monobrand_channel,
            multibrand_channels=multibrand_channel,
            daily_capacity=daily_capacity,
            non_prescriber_included=(is_non_prescriber == "Yes"),
            non_prescriber_priority=non_prescriber_priority,
            e_consent_rte=e_consent_rte,
        )
        return capacity_dto, brand_distribution 
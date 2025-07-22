"""HCP envelope matrix and non-prescriber constraints form."""

import streamlit as st
from typing import List, Optional, Tuple
from core.base import PageForm
from core.dto import (
    HistoricalEnvelopeDTO, SegmentEnvelopeDTO, NonPrescriberEnvelopeDTO, HCPEnvelopeRule
)
from ui.ui_utils import inject_global_css_and_header
from services.ui_data_service import UIDataService

class HCPEnvelopeForm(PageForm):
    """Form for HCP envelope matrix and non-prescriber constraints."""
    
    @staticmethod
    def render(
        channels: List[str], 
        brands: List[str], 
        mode: str, 
        use_segment_matrix: bool
    ) -> Tuple[Optional[List[HistoricalEnvelopeDTO]], 
               Optional[List[SegmentEnvelopeDTO]], 
               Optional[List[NonPrescriberEnvelopeDTO]]]:
        inject_global_css_and_header(logo_path="./utils/turing_logo.PNG")
        st.markdown(
            """
            <div class="tooltip">
                <h5>HCP Capacity Constraints for Upcoming Cycle:</h5>
                <span class="tooltiptext">Provide the minimum and maximum interaction limits based on reference data for the channel. For example, if HCP has had 1 interaction in the reference cycle/ segment level then the minimum and maximum interaction should be around the permissible range that seems feasible, like 1 and 4</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        toggle_option = st.radio(
            "Select from the options below at which level the envelope matrix should be provided:",
            ("Historical Interaction level", "HCP Segment level"),
            horizontal=True,
        )
        use_segment_matrix = toggle_option == "HCP Segment level"
        historical_envelopes = []
        segment_envelopes = []
        non_prescriber_envelopes = []
        if not use_segment_matrix:
            for channel in channels:
                st.markdown(f"<h5>HCP Constraints for {channel}</h5>", unsafe_allow_html=True)
                df = st.data_editor(
                    [{"Reference Cycle Actual": i, "Min": 0, "Max": 0} for i in range(5)],
                    num_rows="dynamic",
                    key=f"hist_env_{channel}"
                )
                for _, row in df.iterrows():
                    rule = HCPEnvelopeRule(min_val=row["Min"], max_val=row["Max"])
                    historical_envelopes.append(
                        HistoricalEnvelopeDTO(
                            channel=channel,
                            reference_cycle_actual=row["Reference Cycle Actual"],
                            rule=rule
                        )
                    )
            from services.business_constraints_service import BusinessConstraintsService
            try:
                BusinessConstraintsService.validate_envelope_matrix(historical_envelopes)
            except ValueError as e:
                st.error(str(e))
                return None, None, None
        else:
            segments = ["A", "B", "C", "D"]
            for brand in brands:
                st.markdown(f"<ul><li><h5>Input the min/max interactions for {brand}</h5></li></ul>", unsafe_allow_html=True)
                cols = st.columns(len(channels))
                for idx, channel in enumerate(channels):
                    with cols[idx]:
                        st.markdown(f"<b>{channel}</b>", unsafe_allow_html=True)
                        df = st.data_editor(
                            [{"Segment": seg, "Min": 0, "Max": 0} for seg in segments],
                            num_rows="dynamic",
                            key=f"seg_env_{brand}_{channel}"
                        )
                        for _, row in df.iterrows():
                            rule = HCPEnvelopeRule(min_val=row["Min"], max_val=row["Max"])
                            segment_envelopes.append(
                                SegmentEnvelopeDTO(
                                    channel=channel,
                                    brand=brand,
                                    segment=row["Segment"],
                                    rule=rule
                                )
                            )
            from services.business_constraints_service import BusinessConstraintsService
            try:
                BusinessConstraintsService.validate_envelope_matrix(segment_envelopes)
            except ValueError as e:
                st.error(str(e))
                return None, None, None
        st.markdown(
            """
            <div class="tooltip">
                <h5>(B) Inputs for Non-Prescribers</h5>
            </div>
            """,
            unsafe_allow_html=True,
        )
        is_non_prescriber = st.radio(
            "Is Non-prescriber included in the Target list for Envelope?",
            ("No", "Yes"),
            horizontal=True,
            key="non_prescriber_envelope_radio"
        )
        if is_non_prescriber == "Yes":
            non_prescriber_input_msg = "For non-prescribers, input the min/max interactions limits"
            if mode != "Monobrand":
                non_prescriber_input_msg += " (For All Brands)"
            st.write(f"{non_prescriber_input_msg}.")
            df = st.data_editor(
                [{"Channel": channel, "Min": 0, "Max": 0} for channel in channels],
                num_rows="dynamic",
                key="np_env"
            )
            for _, row in df.iterrows():
                rule = HCPEnvelopeRule(min_val=row["Min"], max_val=row["Max"])
                non_prescriber_envelopes.append(
                    NonPrescriberEnvelopeDTO(channel=row["Channel"], rule=rule)
                )
            from services.business_constraints_service import BusinessConstraintsService
            try:
                BusinessConstraintsService.validate_envelope_matrix(non_prescriber_envelopes)
            except ValueError as e:
                st.error(str(e))
                return None, None, None
        st.session_state.use_segment_matrix = use_segment_matrix
        st.session_state.historical_envelopes = historical_envelopes
        st.session_state.segment_envelopes = segment_envelopes
        st.session_state.non_prescriber_envelopes = non_prescriber_envelopes
        return (
            historical_envelopes if not use_segment_matrix else None,
            segment_envelopes if use_segment_matrix else None,
            non_prescriber_envelopes if is_non_prescriber == "Yes" else None
        ) 
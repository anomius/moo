"""Review and submission service for OCCP constraints."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from core.dto import DTOBundle
from core.logging import init_logger

logger = init_logger()

class ReviewSubmissionService:
    """Service for reviewing and submitting OCCP constraints."""
    
    def __init__(self):
        """Initialize the review submission service."""
        self.user_email: Optional[str] = None
    
    @st.dialog("Constraints Summary", width="large")
    def show_review_dialog(
        self,
        bundle: DTOBundle,
        final_hcp_bounds: pd.DataFrame,
        final_edited_non_prescribers_constraints_df: pd.DataFrame,
        output_table_dict: Dict[str, pd.DataFrame]
    ):
        """
        Show a dialog for reviewing constraints before submission.
        
        Args:
            bundle: Complete DTO bundle with all OCCP constraints
            final_hcp_bounds: DataFrame with HCP bounds data
            final_edited_non_prescribers_constraints_df: DataFrame with non-prescriber constraints
            output_table_dict: Dictionary of output tables for Snowflake
        """
        self._render_market_details(bundle)
        self._render_cycle_details(bundle)
        self._render_reference_cycle_details(bundle)
        self._render_channel_details(bundle)
        self._render_rep_capacity_constraints(bundle)
        self._render_hcp_constraints(final_hcp_bounds)
        self._render_non_prescribers_details(bundle, final_edited_non_prescribers_constraints_df)
        self._render_email_section(output_table_dict)
    
    def _render_market_details(self, bundle: DTOBundle):
        """Render market and brand details section."""
        self._render_header("1. Market & Brand Details:")
        details = {
            "Country": bundle.market.country,
            "Brands": ", ".join(bundle.market.brands),
            "Sales Line": bundle.market.sales_line,
        }
        st.markdown("\n".join([f"* **{k}**: {v}" for k, v in details.items()]))
        if bundle.market.mode == "Multibrand" and bundle.market.specialties:
            for brands_str, specialty in bundle.market.specialties.items():
                st.markdown(
                    f"* **Specialties for {brands_str} that can be promoted together**: {specialty}"
                )
    
    def _render_cycle_details(self, bundle: DTOBundle):
        """Render upcoming cycle details section."""
        self._render_header("2. Upcoming Cycle Details")
        details = {
            "Cycle Name": bundle.cycle.name,
            "Cycle Length (in months)": str(bundle.cycle.months),
            "Cycle Start Date": str(bundle.cycle.start),
            "Working Days in Upcoming Cycle": str(bundle.cycle.working_days),
        }
        st.markdown("\n".join([f"* **{k}**: {v}" for k, v in details.items()]))
    
    def _render_reference_cycle_details(self, bundle: DTOBundle):
        """Render reference cycle details section."""
        self._render_header("3. Reference Cycle Details")
        details = {
            "Cycle Length (in months)": str(bundle.reference.months),
            "Cycle Start Date": str(bundle.reference.start),
            "Working Days in Reference Cycle": str(bundle.reference.working_days),
        }
        st.markdown("\n".join([f"* **{k}**: {v}" for k, v in details.items()]))
    
    def _render_channel_details(self, bundle: DTOBundle):
        """Render channel selection details section."""
        self._render_header("4. Channel Details")
        if bundle.market.mode == "Monobrand":
            st.markdown(
                f"**OCCP channels in scope**: {', '.join(bundle.capacity.channels)}"
            )
        elif bundle.market.mode == "Multibrand":
            st.markdown(
                f"* **OCCP channels in scope**: {', '.join(bundle.capacity.channels)}"
            )
            st.markdown(
                f"* **Channels for Multibrand OCCP only**: {', '.join(bundle.capacity.multibrand_channels)}"
            )
    
    def _render_rep_capacity_constraints(self, bundle: DTOBundle):
        """Render REP capacity constraints section."""
        self._render_header("5. REP Capacity Constraints")
        rep_capacity_dict = self._get_rep_capacity_dict(bundle)
        st.markdown(
            "\n".join([f"* **{k}**: {v}" for k, v in rep_capacity_dict.items()])
        )
    
    def _get_rep_capacity_dict(self, bundle: DTOBundle) -> Dict[str, float]:
        """Build REP capacity details dictionary."""
        rep_capacity_dict = {}
        for channel in bundle.capacity.channels:
            if bundle.capacity.non_prescriber_included:
                rep_capacity_dict[
                    f"Avg {channel} interactions per day (Prescriber & Non-Prescriber combined)"
                ] = bundle.capacity.daily_capacity.get(channel, 0.0)
            else:
                rep_capacity_dict[f"Avg {channel} interactions per day"] = bundle.capacity.daily_capacity.get(channel, 0.0)
        return rep_capacity_dict
    
    def _render_hcp_constraints(self, final_hcp_bounds: pd.DataFrame):
        """Render HCP constraints tables for each channel."""
        if "REFERENCE_CYCLE_ACTUAL" in final_hcp_bounds.columns:
            for group, subset in final_hcp_bounds.groupby("CHANNEL"):
                self._render_header(f"6. HCP Constraints for {group} ")
                st.markdown(
                    subset.to_html(
                        index=False,
                        columns=["REFERENCE_CYCLE_ACTUAL", "MIN_VALUE", "MAX_VALUE"],
                    ),
                    unsafe_allow_html=True,
                )
        elif "SEGMENT" in final_hcp_bounds.columns:
            for group, subset in final_hcp_bounds.groupby(["CHANNEL", "BRAND"]):
                channel, brand = group 
                self._render_header(f"6. HCP Constraints for {channel} | Brand: {brand}")
                st.markdown(
                    subset.to_html(
                        index=False,
                        columns=["SEGMENT", "MIN_VALUE", "MAX_VALUE"],
                    ),
                    unsafe_allow_html=True,
                )
    
    def _render_non_prescribers_details(
        self, 
        bundle: DTOBundle, 
        final_edited_non_prescribers_constraints_df: pd.DataFrame
    ):
        """Render non-prescribers details section."""
        self._render_header("7. Non-Prescribers Details")
        st.markdown(
            f"* **Is Non-prescriber included in the Target list**: {'Yes' if bundle.capacity.non_prescriber_included else 'No'}"
        )
        if bundle.capacity.non_prescriber_included:
            st.markdown(
                f"* **Non-Prescribers priority**: {bundle.capacity.non_prescriber_priority}"
            )

            self._render_header("8. Non-Prescribers Constraints")
            non_prescribers_html_table = final_edited_non_prescribers_constraints_df.rename(
                columns={"Channel": "CHANNEL", "Min": "MIN_VALUE", "Max": "MAX_VALUE"}
            ).to_html(index=False)
            st.markdown(
                non_prescribers_html_table,
                unsafe_allow_html=True,
            )
    
    def _render_email_section(self, output_table_dict: Dict[str, pd.DataFrame]):
        """Render the email input and submission section."""
        columns = st.columns((1, 0.75, 1))
        with columns[0]:
            st.warning(
                "**Note:** In case of multiple email recipients, please input the email ids as comma-separated values."
            )
            self.user_email = st.text_input(
                "Provide your email address to receive a copy of the business constraints:"
            )
            if not self.user_email:
                st.warning("Provide your email address")
                return
            if not self.user_email.endswith("@sanofi.com"):
                st.warning("Please provide a valid sanofi email address.")
                return
            if st.button("Submit Business Constraints"):
                with st.spinner("Submitting..."):
                    # TODO: Implement submission logic
                    st.success("Business constraints submitted successfully!")
            else:
                st.warning(
                    "Click on this button to share the Business Constraints with the OCCP team"
                )
    
    def _render_header(self, header_text: str):
        """Render a colored section header in the review dialog."""
        st.markdown(
            f'<h2 style="color: #7a00e6;">{header_text}</h2>',
            unsafe_allow_html=True,
        )
    
    def format_email_message(self, bundle: DTOBundle) -> tuple[str, str]:
        """
        Format the subject and body for the business constraints email.
        
        Args:
            bundle: Complete DTO bundle
            
        Returns:
            Tuple of (subject, body)
        """
        if len(bundle.market.brands) == 1:
            subject = (
                "Business Constraints Submission for Review | "
                + str(bundle.market.country)
                + ", "
                + str(bundle.market.brands[0])
            )
            email_body = f"""<html>
                <head></head>
                <body>
                <h5><span lang=EN style='font-family:"Noto Sans",sans-serif;mso-fareast-font-family:"Times New Roman";color:#000000;mso-ansi-language:EN;font-weight:normal'>
                Hi,<br><br>
                We would like to inform you that a user has submitted the business constraints for the following details:
                <ul>
                <li>Country : <b>{bundle.market.country}</b> </li> 
                <li>Brand : <b>{bundle.market.brands[0]}</b> </li>
                <li>Sales Line : <b>{bundle.market.sales_line}</b> </li>
                <li>Cycle Name : <b>{bundle.cycle.name}</b> </li>
                </ul>
                <br>
                Please find the attached Excel file containing the detailed constraints submitted through the OCCP Business Constraints Tool for your review.
                <br><br>
                Thank you for your attention to this matter.
                <br><br>
                Regards,
                <br>
                OCCP Business Constraints Tool
                <o:p></o:p></span></h5></body></html>"""
        else:
            brands = ", ".join(bundle.market.brands)
            subject = (
                "Business Constraints Submission for Review | "
                + str(bundle.market.country)
                + " | "
                + brands
            )
            email_body = f"""<html>
                <head></head>
                <body>
                <h5><span lang=EN style='font-family:"Noto Sans",sans-serif;mso-fareast-font-family:"Times New Roman";color:#000000;mso-ansi-language:EN;font-weight:normal'>
                Hi,<br><br>
                We would like to inform you that a user has submitted the business constraints for the following details:
                <ul>
                <li>Country : <b>{bundle.market.country}</b> </li> 
                <li>Brands : <b>{brands}</b> </li>
                <li>Sales Line : <b>{bundle.market.sales_line}</b> </li>
                <li>Cycle Name : <b>{bundle.cycle.name}</b> </li>
                </ul>
                <br>
                Please find the attached Excel file containing the detailed constraints submitted through the OCCP Business Constraints Tool for your review.
                <br><br>
                Thank you for your attention to this matter.
                <br><br>
                Regards,
                <br>
                OCCP Business Constraints Tool
                <o:p></o:p></span></h5></body></html>"""

        return subject, email_body 
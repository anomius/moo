"""Review and submission service for OCCP constraints."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from core.dto import DTOBundle
from core.logging import init_logger
from infra.email_service import EmailService
from infra.excel_exporter import ExcelExporterService
from infra.snowflake_repo import SnowflakeRepo
from turing_generic_lib.utils.config import TuringConfig
import os
import yaml
from infra.api_client import ApiClient

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
    
    def submit_constraints(self, bundle: DTOBundle, output_table_dict: Dict[str, pd.DataFrame]) -> str:
        """
        Orchestrate Excel generation, API call, email sending, and Snowflake push for OCCP constraints.
        Returns a status message for user feedback.
        """
        try:
            # 1. Generate Excel file
            excel_exporter = ExcelExporterService()
            excel_bytes = excel_exporter.build(bundle)
            filename = f"Business_Constraints_{bundle.market.country}_{'_'.join(bundle.market.brands)}_{bundle.cycle.name}.xlsx"

            # 2. Load email config
            config_path = os.path.join(os.path.dirname(__file__), '../config/email_config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                email_config = yaml.safe_load(f)
            env = os.environ.get("ENVIRONMENT", "DEV")
            country_code = bundle.market.country[:2].upper()
            if env == "PROD":
                recipients = email_config.get("to", {}).get("emails", []).copy()
                country_specific = (
                    email_config.get("to", {}).get("gen", {}).get(country_code, {}).get("emails", [])
                )
                recipients.extend([e for e in country_specific if e not in recipients])
            else:
                recipients = email_config.get("test", {}).get("emails", []).copy()
            if self.user_email and self.user_email not in recipients:
                recipients.append(self.user_email)
            # 3. Prepare email subject/body
            email_service = EmailService(
                smtp_gateway=email_config["SMTP_GATEWAY"][0],
                smtp_port=int(email_config["SMTP_PORT"][0]),
                email_from=email_config["from"][0],
                email_password=os.environ.get("EMAIL_PWD", "")
            )
            subject = email_service.format_email_subject(bundle.market.country, bundle.market.brands)
            body = email_service.format_email_body(
                bundle.market.country, bundle.market.brands, bundle.market.sales_line, bundle.cycle.name
            )

            # 4. Call OCCP optimization API
            api_client = ApiClient.create_for_environment(env)
            api_response = api_client.post_bundle(bundle)
            if api_response.get("status") != "success":
                return f"API submission failed: {api_response.get('data', 'Unknown error')}"

            # 5. Send email
            email_service.send(subject, body, recipients, excel_bytes, filename)
            # 6. Push output tables to Snowflake
            config = TuringConfig(config_dir=None, gbu="gen", countrycode=country_code, brand=bundle.market.brands[0])
            config.load()
            snowflake_repo = SnowflakeRepo(config)
            for table, df in output_table_dict.items():
                if df is not None and not df.empty:
                    df.to_sql(table, snowflake_repo.snowflake_con, if_exists='append', index=False)
            return "Business constraints submitted, API called, emailed, and pushed to Snowflake successfully!"
        except Exception as ex:
            logger.error(f"Submission failed: {ex}")
            return f"Submission failed: {ex}"

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
                    # Call the new orchestration method
                    status = self.submit_constraints(self.bundle, output_table_dict)
                    if status.startswith("Submission failed"):
                        st.error(status)
                    else:
                        st.success(status)
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
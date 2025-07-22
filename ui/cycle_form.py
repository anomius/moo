"""Cycle and reference cycle selection form."""

import streamlit as st
from datetime import date
from dateutil import relativedelta
from core.base import PageForm
from core.dto import CycleDTO, ReferenceCycleDTO
from ui.ui_utils import inject_global_css_and_header

class CycleForm(PageForm):
    """Form for cycle and reference cycle selection."""
    
    @staticmethod
    def render() -> tuple[CycleDTO, ReferenceCycleDTO]:
        inject_global_css_and_header(logo_path="./utils/turing_logo.PNG")
        st.markdown(
            ("<div><h3>Upcoming Cycle Details:</h3></div>"),
            unsafe_allow_html=True,
        )
        today = date.today()
        next_year = today.year
        cycle_start_input = st.text_input(
            "Select the Start Date (YYYY/MM)",
            value=f"{next_year}/01",
            help="Select the start date for the upcoming Omni Channel Call Plan (OCCP)  cycle in YYYY/MM format.",
        )
        try:
            year, month = map(int, cycle_start_input.split("/"))
            start_date = date(year, month, 1)
        except ValueError:
            st.error("Please enter the date in YYYY/MM format.")
            return None, None
        cycle_length = st.number_input(
            "Select the Cycle Length (in months)",
            min_value=1,
            max_value=12,
            value=1,
            step=1,
            format="%d",
            help="Select the duration of the upcoming Omni Channel Call Plan (OCCP) cycle. Options are 1, 3, 4, or 6 months.",
        )
        cycle_end = start_date + relativedelta.relativedelta(months=cycle_length + 1, days=-1)
        if cycle_length > 1:
            cycle_name = f"C{(start_date.month//cycle_length)+1} {start_date.year}"
        elif cycle_length == 1:
            cycle_name = f"C{(start_date.month//cycle_length)} {start_date.year}"
        working_days = st.number_input(
            "Enter the number of Working Days (in days)",
            min_value=1,
            max_value=(cycle_end - start_date).days,
            value=1,
            step=1,
            format="%d",
            help="Enter the number of Working Days for the upcoming Omni Channel Call Plan (OCCP) cycle",
        )
        st.markdown(
            (
                "<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'>"
                "<div>"
                "<h3>Reference Cycle Details : <i class='fa fa-info-circle' aria-hidden='true' "
                "title='Reference cycle details are used to compare the Turing OCCP output for the upcoming cycle with the reference cycle OCCP. "
                "The OCCP output for the upcoming cycle is generated using the entire historical data.'></i></h3>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        ref_start_input = st.text_input(
            "Select the Start Date (YYYY/MM)",
            value=f"{next_year-1}/01",
            help="Select the start date for the reference Omni Channel Call Plan (OCCP) cycle in YYYY/MM format.",
        )
        try:
            ref_year, ref_month = map(int, ref_start_input.split("/"))
            ref_start_date = date(ref_year, ref_month, 1)
        except ValueError:
            st.error("Please enter the date in YYYY/MM format.")
            return None, None
        ref_length = st.number_input(
            "Select the Cycle Length (in months)",
            min_value=1,
            max_value=12,
            value=1,
            step=1,
            format="%d",
            help="Select the duration of the reference Omni Channel Call Plan (OCCP) cycle. Options are 1, 3, 4, or 6 months.",
        )
        if ref_length != cycle_length:
            st.warning(
                "**Note:**: Please verify, the reference cycle length and upcoming cycle length values are different."
            )
        ref_end_date = ref_start_date + relativedelta.relativedelta(months=ref_length)
        ref_working_days = st.number_input(
            "Enter the number of Working Days (in days)",
            min_value=1,
            max_value=(ref_end_date - ref_start_date).days,
            value=1,
            step=1,
            format="%d",
            help="Enter the number of Working Days for the reference Omni Channel Call Plan (OCCP) cycle",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(
            '''
            <div class="custom-list">
                <h5>For OCCP calculation, we follow Customer Facing Guidance for effort allocation as:</h5>
                <ul>
                    <li>Segment A: 40-50%</li>
                    <li>Segment B: 20-30%</li>
                    <li>Segment C: 10-15%</li>
                </ul>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        cycle = CycleDTO(
            name=cycle_name,
            start=start_date,
            end=cycle_end,
            months=cycle_length,
            working_days=working_days,
        )
        reference = ReferenceCycleDTO(
            start=ref_start_date,
            end=ref_end_date,
            months=ref_length,
            working_days=ref_working_days,
        )
        return cycle, reference 
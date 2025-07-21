"""Cycle and reference cycle selection form."""

import streamlit as st
from datetime import date
from dateutil import relativedelta
from core.base import PageForm
from core.dto import CycleDTO, ReferenceCycleDTO
from ui.page import inject_global_css_and_header

class CycleForm(PageForm):
    """Form for cycle and reference cycle selection."""
    
    @staticmethod
    def render() -> tuple[CycleDTO, ReferenceCycleDTO]:
        """
        Render the cycle and reference cycle selection UI.
        
        Returns:
            Tuple of (CycleDTO, ReferenceCycleDTO) with selected cycle information
        """
        inject_global_css_and_header(logo_path="./utils/turing_logo.PNG")
        # Upcoming cycle details
        st.markdown(
            ("<div class='tooltip'><h3>Upcoming Cycle Details:</h3></div>"),
            unsafe_allow_html=True,
        )
        
        today = date.today()
        next_year = today.year
        
        # Cycle start date
        cycle_start_input = st.text_input(
            "Select the Start Date (YYYY/MM)",
            value=f"{next_year}/01",
            help="Select the start date for the upcoming OCCP cycle in YYYY/MM format."
        )
        
        try:
            year, month = map(int, cycle_start_input.split("/"))
            start_date = date(year, month, 1)
        except ValueError:
            st.error("Please enter the date in YYYY/MM format.")
            return None, None
        
        # Cycle length
        cycle_length = st.number_input(
            "Select the Cycle Length (in months)",
            min_value=1,
            max_value=12,
            value=1,
            step=1,
            format="%d",
            help="Select the duration of the upcoming OCCP cycle."
        )
        
        # Calculate cycle end date
        cycle_end = start_date + relativedelta.relativedelta(months=cycle_length, days=-1)
        
        # Cycle name
        if cycle_length > 1:
            cycle_name = f"C{(start_date.month//cycle_length)+1} {start_date.year}"
        else:
            cycle_name = f"C{start_date.month} {start_date.year}"
        
        # Working days
        working_days = st.number_input(
            "Enter the number of Working Days (in days)",
            min_value=1,
            max_value=31*cycle_length,
            value=1,
            step=1,
            format="%d",
            help="Enter the number of Working Days for the upcoming OCCP cycle."
        )
        
        # Reference cycle details
        st.markdown(
            (
                "<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'>"
                "<div class='tooltip'>"
                "<h3>Reference Cycle Details : <i class='fa fa-info-circle' aria-hidden='true' "
                "title='Reference cycle details are used to compare the Turing OCCP output for the upcoming cycle with the reference cycle OCCP. "
                "The OCCP output for the upcoming cycle is generated using the entire historical data.'></i></h3>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        
        # Reference cycle start date
        ref_start_input = st.text_input(
            "Select the Reference Start Date (YYYY/MM)",
            value=f"{next_year-1}/01",
            help="Select the start date for the reference OCCP cycle in YYYY/MM format."
        )
        
        try:
            ref_year, ref_month = map(int, ref_start_input.split("/"))
            ref_start_date = date(ref_year, ref_month, 1)
        except ValueError:
            st.error("Please enter the reference date in YYYY/MM format.")
            return None, None
        
        # Reference cycle length
        ref_length = st.number_input(
            "Select the Reference Cycle Length (in months)",
            min_value=1,
            max_value=12,
            value=1,
            step=1,
            format="%d",
            help="Select the duration of the reference OCCP cycle."
        )
        
        # Calculate reference cycle end date
        ref_end = ref_start_date + relativedelta.relativedelta(months=ref_length, days=-1)
        
        # Reference working days
        ref_working_days = st.number_input(
            "Enter the number of Working Days for Reference Cycle (in days)",
            min_value=1,
            max_value=31*ref_length,
            value=1,
            step=1,
            format="%d",
            help="Enter the number of Working Days for the reference OCCP cycle."
        )
        
        # Warning if cycle lengths differ
        if ref_length != cycle_length:
            st.warning(
                "**Note:** Please verify, the reference cycle length and upcoming cycle length values are different."
            )
        
        # Store in session state for persistence
        st.session_state.cycle_start_date = start_date
        st.session_state.cycle_length = cycle_length
        st.session_state.cycle_end_date = cycle_end
        st.session_state.cycle_name = cycle_name
        st.session_state.working_days = working_days
        st.session_state.ref_start_date = ref_start_date
        st.session_state.ref_length = ref_length
        st.session_state.ref_end_date = ref_end
        st.session_state.ref_working_days = ref_working_days
        
        # Build and return DTOs
        cycle = CycleDTO(
            name=cycle_name,
            start=start_date,
            end=cycle_end,
            months=cycle_length,
            working_days=working_days
        )
        
        reference = ReferenceCycleDTO(
            start=ref_start_date,
            end=ref_end,
            months=ref_length,
            working_days=ref_working_days
        )
        
        # Add segment guidance at the end
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
        
        return cycle, reference 
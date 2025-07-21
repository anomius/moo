import streamlit as st
import os
import base64
from core.dto import CountryBrandDTO, BrandDTO, CycleDTO, ReferenceCycleDTO
from datetime import date
from dateutil import relativedelta

def inject_global_css_and_header(logo_path=None):
    """
    Inject global CSS and OCCP header bar (with logo if provided).
    Call this at the top of every form's render method.
    """
    # Tooltip and custom styles
    st.markdown(
        '''
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted #7a00e6;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 320px;
            background-color: #f9f9f9;
            color: #333;
            text-align: left;
            border-radius: 6px;
            border: 1px solid #7a00e6;
            padding: 8px 12px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -160px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 14px;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        .top-header {
            display: flex;
            align-items: center;
            background: #f5f0ff;
            padding: 1rem 2rem 1rem 1rem;
            border-radius: 0 0 12px 12px;
            margin-bottom: 1.5rem;
        }
        .top-header h1 {
            color: #7a00e6;
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0 1.5rem 0 0;
            letter-spacing: 1px;
        }
        .top-header img {
            height: 48px;
            margin-left: auto;
        }
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
        ''',
        unsafe_allow_html=True,
    )
    # Header bar with logo
    logo_html = ""
    if logo_path and os.path.exists(logo_path):
        with open(logo_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode()
        logo_html = f"<img src='data:image/png;base64,{base64_image}' alt='Turing Logo'>"
    st.markdown(
        f"""
        <div class='top-header'>
            <h1>OCCP Business Constraints Tool</h1>
            {logo_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def sidebar_market_brand_form():
    """
    Collect country, brand(s), sales line, mode, and specialties from the sidebar.
    Return a CountryBrandDTO.
    """
    # Placeholder lists (replace with real data as needed)
    countries = ["Italy", "France", "Germany", "Spain"]
    country_codes = {"Italy": "IT", "France": "FR", "Germany": "DE", "Spain": "ES"}
    sales_lines = ["IT_Diab_PM", "FR_Onco_PM", "DE_Cardio_PM", "ES_Resp_PM"]
    all_brands = [
        BrandDTO(name="BrandA", brand_code="A", brand_id="BRAND1"),
        BrandDTO(name="BrandB", brand_code="B", brand_id="BRAND2"),
        BrandDTO(name="BrandC", brand_code="C", brand_id="BRAND3"),
    ]
    brand_names = [b.name for b in all_brands]

    with st.sidebar:
        country = st.selectbox("Select Country", countries)
        country_code = country_codes[country]
        sales_line = st.selectbox("Select Sales Line", [s for s in sales_lines if s.startswith(country_code)])
        mode = st.radio("OCCP Mode", ("Monobrand", "Multibrand"), horizontal=True)
        if mode == "Monobrand":
            selected_brand_names = [st.selectbox("Select Brand", brand_names)]
        else:
            selected_brand_names = st.multiselect("Select Brands", brand_names)
        selected_brands = [b for b in all_brands if b.name in selected_brand_names]
        specialties = None
        if mode == "Multibrand" and selected_brands:
            specialties_input = st.text_input("Specialties for selected brands (comma-separated)")
            if specialties_input:
                specialties = {" and ".join(selected_brand_names): specialties_input}
    return CountryBrandDTO(
        country=country,
        country_code=country_code,
        sales_line=sales_line,
        brands=selected_brands,
        mode=mode,
        specialties=specialties,
    )

def sidebar_cycle_form():
    """
    Collect cycle and reference cycle configuration from the sidebar.
    Return (CycleDTO, ReferenceCycleDTO).
    """
    with st.sidebar:
        today = date.today()
        next_year = today.year
        # Cycle
        st.markdown("<h4>Upcoming Cycle</h4>", unsafe_allow_html=True)
        cycle_start_input = st.text_input(
            "Start Date (YYYY/MM)", value=f"{next_year}/01",
            help="Start date for the upcoming OCCP cycle."
        )
        try:
            year, month = map(int, cycle_start_input.split("/"))
            start_date = date(year, month, 1)
        except Exception:
            st.error("Please enter the date in YYYY/MM format.")
            return None, None
        cycle_length = st.number_input(
            "Cycle Length (months)", min_value=1, max_value=12, value=1, step=1, format="%d"
        )
        cycle_end = start_date + relativedelta.relativedelta(months=cycle_length, days=-1)
        if cycle_length > 1:
            cycle_name = f"C{(start_date.month//cycle_length)+1} {start_date.year}"
        else:
            cycle_name = f"C{start_date.month} {start_date.year}"
        working_days = st.number_input(
            "Working Days (upcoming cycle)", min_value=1, max_value=31*cycle_length, value=1, step=1, format="%d"
        )
        # Reference Cycle
        st.markdown("<h4>Reference Cycle</h4>", unsafe_allow_html=True)
        ref_start_input = st.text_input(
            "Reference Start Date (YYYY/MM)", value=f"{next_year-1}/01",
            help="Start date for the reference OCCP cycle."
        )
        try:
            ref_year, ref_month = map(int, ref_start_input.split("/"))
            ref_start_date = date(ref_year, ref_month, 1)
        except Exception:
            st.error("Please enter the reference date in YYYY/MM format.")
            return None, None
        ref_length = st.number_input(
            "Reference Cycle Length (months)", min_value=1, max_value=12, value=1, step=1, format="%d"
        )
        ref_end = ref_start_date + relativedelta.relativedelta(months=ref_length, days=-1)
        ref_working_days = st.number_input(
            "Working Days (reference cycle)", min_value=1, max_value=31*ref_length, value=1, step=1, format="%d"
        )
        if ref_length != cycle_length:
            st.warning("Reference and upcoming cycle lengths differ.")
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
    return cycle, reference

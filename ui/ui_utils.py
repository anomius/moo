import streamlit as st
import os
import base64
from core.dto import CountryBrandDTO, BrandDTO, CycleDTO, ReferenceCycleDTO
from datetime import date
from dateutil import relativedelta
from ui.market_brand_form import MarketBrandForm
from ui.cycle_form import CycleForm

def inject_global_css_and_header(logo_path=None):
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
    with st.sidebar:
        return MarketBrandForm.render()

def sidebar_cycle_form():
    with st.sidebar:
        return CycleForm.render() 
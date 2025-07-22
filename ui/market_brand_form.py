import streamlit as st
from services.ui_data_service import UIDataService
from core.dto import CountryBrandDTO, BrandDTO

class MarketBrandForm:
    @staticmethod
    def render() -> CountryBrandDTO:
        st.markdown("<h3>Market & Brand Details</h3>", unsafe_allow_html=True)
        countries = UIDataService.get_countries()
        country = st.selectbox(
            "Select the Country Name",
            countries,
            help=(
                "Select the country for which the Omni Channel Call Plan (OCCP) "
                "needs to be generated for the upcoming cycle."
            ),
        )
        sales_lines = UIDataService.get_sales_lines_for_country(country)
        sales_line = st.selectbox(
            "Select the Sales Line Name",
            sales_lines,
            help="Select the sales line name for the upcoming Omni Channel Call Plan (OCCP) cycle for the chosen country.",
        )
        mode = st.radio(
            "Choose the OCCP type",
            ["Monobrand", "Multibrand"],
            horizontal=True,
            help="Specify whether the Omni Channel Call Plan (OCCP) is for a single brand (Monobrand) or multiple brands (Multibrand).",
        )
        brands = UIDataService.get_brand_list_with_indications()
        if mode == "Monobrand":
            selected_brand_names = [st.selectbox(
                "Select the brand name",
                brands,
                help="Choose a brand for the upcoming Omni Channel Call Plan (OCCP) cycle. If the brand name is not listed, contact the OCCP Support team.",
            )]
        else:
            selected_brand_names = st.multiselect(
                "Select the brand names",
                brands,
                help="Choose brands for the upcoming Omni Channel Call Plan (OCCP) cycle. If the brand name is not listed, contact the OCCP Support team.",
            )
        selected_brands = [BrandDTO(name=b, brand_code=b, brand_id=f"BRAND{i+1}") for i, b in enumerate(selected_brand_names)]
        specialties = None
        if mode == "Multibrand" and selected_brands:
            brands_str = " and ".join(selected_brand_names)
            specialty = st.text_input(
                f"Please specify Specialties for {brands_str} that can be promoted together."
            )
            st.warning(
                "**Note:** In case of multiple specialties, please input the text as comma-separated values."
            )
            if specialty:
                specialties = {brands_str: specialty}
        return CountryBrandDTO(
            country=country,
            country_code=country[:2].upper(),  # You may want to map this properly
            sales_line=sales_line,
            brands=selected_brands,
            mode=mode,
            specialties=specialties,
        ) 
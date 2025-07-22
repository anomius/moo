"""Snowflake Output Mapping

This module provides functionality to store the constraints
in following tables DS_BUSINESS_CONSTRAINTS, DS_BRAND_SPECIFIC_BUSINESS_CONSTRAINTS,
DS_OCCP_HCP_CONSTRAINTS
"""
import pandas as pd
from turing_generic_lib.utils.snowflake_connection import push_df_to_snowflake
from turing_generic_lib.utils.logging import get_logger
from datetime import datetime
import uuid
import re
import calendar

APP_NAME = "OCCPTool"
LOGGER = get_logger(APP_NAME)

# --- Universal value extraction helpers ---

def get_latest_id_from_snowflake(table_name, conn):
    """
    Fetch the highest numeric part from IDs like 'C_000123' in the given table.
    Returns the next integer to use.
    """
    query = f"SELECT MAX(ID) AS MAX_ID FROM {table_name}"
    df = pd.read_sql(query,conn)
    max_id = df['MAX_ID'].iloc[0]
    if pd.isnull(max_id):
        return 1
    match = re.match(r"C_(\d+)", max_id)
    if match:
        return int(match.group(1)) + 1
    return 1

def parse_brand_distribution(distribution_str):
    """
    Parses a string like '50% SOLIQUA, 50% TOUJEO' into a dict:
    {'SOLIQUA': '50', 'TOUJEO': '50'}
    """
    result = {}
    if not distribution_str:
        return result
    parts = [p.strip() for p in distribution_str.split(',')]
    for part in parts:
        match = re.match(r'(\d+)%\s*(.+)', part)
        if match:
            percent, brand = match.groups()
            result[brand.strip().upper()] = percent.strip()
    return result

def get_value(data, info, col_info='Information', col_value='Values'):
    """
    Extract value for a given info string from either a DataFrame or a list-of-lists.
    """
    if isinstance(data, pd.DataFrame):
        mask = data[col_info].str.contains(info, case=False, na=False)
        if mask.any():
            return data.loc[mask, col_value].iloc[0]
        return None
    elif isinstance(data, list):
        for row in data:
            if len(row) >= 3 and info.lower() in row[1].lower():
                return row[2]
        return None
    else:
        raise ValueError("Unsupported data type for get_value")

def get_specialty(data, brands):
    """
    Extract value for a given info string from speciality list-of-lists.
    """
    for row in data:
        if len(row) >= 3 and 'Specify Specialities that can be promoted together' in row[1]:
            # Split by colon, get left and right parts
            if ':' in row[2]:
                brand_part, specialty = row[2].split(':', 1)
                # Check if all brands are present in the brand_part (case-insensitive)
                if all(b.lower() in brand_part.lower() for b in brands):
                    return specialty.strip()
    return None

def get_avg_rep_capacity(data, channel):
    """
    Extract the average representative capacity for a specific channel.
    """
    info_str = f"Avg Rep Capacity per day for {channel}"
    try:
        return float(get_value(data, info_str))
    except Exception:
        return None

def map_channels_with_consent(ui_channels, econsent):
    """
    Maps user interface channel names to standardized channel names.
    """    
    CHANNEL_NAME_MAP = {
        "F2F": "FACE TO FACE",
        "Remote": "REMOTE",
        "Phone": "PHONE",
        "Meetings": "MEETINGS",
        "Virtual Meetings": "VIRTUAL MEETINGS",
        "VIRTUAL_MEETINGS": "VIRTUAL MEETINGS",
        "WHATSAPP/INSTANT_MESSAGE": "WHATSAPP/INSTANT MESSAGE",
        "Whatsapp/Instant Message": "WHATSAPP/INSTANT MESSAGE",
        "RTE-Open": "RTE",
        "RTE-OPEN": "RTE",
        "RTE-Sent": "RTE",
        "RTE-SENT": "RTE",

    }
    mapped = [CHANNEL_NAME_MAP.get(ch, ch) for ch in ui_channels]
    if "RTE" in mapped:
        consent_channel = "RTE WITH CONSENT" if econsent else "RTE WITHOUT CONSENT"
        mapped = [consent_channel if ch == "RTE" else ch for ch in mapped]
    return mapped

def get_channel_id(channel_name, df_channel):
    """
    Returns the CHANNEL_ID for the given channel name.
    """
    channel_name = channel_name.upper().strip()
    df_channel['CHANNEL'] = df_channel['CHANNEL'].str.upper().str.strip()
    result = df_channel.loc[df_channel['CHANNEL'] == channel_name, 'CHANNEL_ID']
    if result.empty:
        raise ValueError(f"Channel '{channel_name}' not found in DS_CHANNEL.")
    return result.values[0]

def get_brand_id(brand_name, df_brand):
    """
    Returns the BRAND_ID for the given brand name.
    If the brand is "DUPIXENT" or starts with "DUPIXENT", it tries to match both BRAND_NAME and INDICATION_NAME.
    """
    brand_name = brand_name.upper().strip()
    df_brand['GLOBAL_BRAND'] = df_brand['GLOBAL_BRAND'].str.upper().str.strip()
    df_brand['INDICATION_NAME'] = df_brand['INDICATION_NAME'].str.upper().str.strip()

    if brand_name.startswith("DUPIXENT"):
        parts = brand_name.split(" ", 1)
        if len(parts) > 1:
            indication = parts[1].strip()
            result = df_brand.loc[
                (df_brand['GLOBAL_BRAND'] == "DUPIXENT") &
                (df_brand['INDICATION_NAME'] == indication),
                'BRAND_ID'
            ]
            if not result.empty:
                return result.values[0]
            else:
                st.error(f"No BRAND_ID found for DUPIXENT with indication '{indication}'.")
        else:
            result = df_brand.loc[df_brand['GLOBAL_BRAND'] == "DUPIXENT", 'BRAND_ID']
            if not result.empty:
                return result.values[0]
            else:
                st.error("No BRAND_ID found for DUPIXENT.")
    else:
        result = df_brand.loc[df_brand['GLOBAL_BRAND'] == brand_name, 'BRAND_ID']
        if result.empty:
            raise ValueError(f"Brand '{brand_name}' not found in DS_BRAND.")
    return result.values[0]

def get_sales_table_id(sales_line, brand_id, occp_type, df_sales_line):
    """
    Returns the SALES_TABLE_ID for the given brand_id, sales_line, and occp_type.
    """
    filtered = df_sales_line[
        (df_sales_line['BRAND_ID'] == brand_id) &
        (df_sales_line['SALES_TEAM'] == sales_line) &
        (df_sales_line['OCCP_TYPE'] == occp_type.upper())
    ]

    if not filtered.empty:
        return filtered.iloc[0]['ID']
    else:
        raise ValueError(f"No SALES_TABLE_ID found for brand_id={brand_id}, sales_line={sales_line}, occp_type={occp_type}")

def get_fact_id(sales_table_id, channel_id, df_master):
    """
    Returns the FACT_ID (M_ID) for the given sales_table_id and channel_id.
    """
    result = df_master.loc[
        (df_master['SALES_TABLE_ID'] == sales_table_id) & (df_master['CHANNEL_ID'] == channel_id), 'M_ID'
    ]
    if result.empty:
        raise ValueError(f"FACT_ID not found for sales_table_id '{sales_table_id}' and channel_id '{channel_id}'.")
    return result.values[0]

def get_canonical_month_date(date_str: str, which: str = 'start'):
    """
    Convert a date string to a canonical date for the start or end of the month.
    """
    date_str = date_str.strip()
    # New: ISO path
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        # Existing Month YYYY path
        for fmt in ('%B %Y', '%b %Y'):
            try:
                dt = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f'Could not parse date: {date_str}')
    year, month = dt.year, dt.month
    if which == 'start':
        return datetime(year, month, 1).date()
    elif which == 'end':
        return datetime(year, month, calendar.monthrange(year, month)[1]).date()
    else:
        raise ValueError("which must be 'start' or 'end'")


def get_time_id(date_str, df_time, which='start'):
    """
    Get the TIME_ID for a given date string from the df_time DataFrame.
    The date string can be in the format 'YYYY-MM-DD' or 'Month YYYY'.
    The 'which' parameter determines if we are looking for the start or end of the month.
    """
    # Get canonical date for the input month
    input_date = get_canonical_month_date(date_str, which=which)

    for idx, row in df_time.iterrows():
        try:
            cycle_date = datetime.strptime(
                str(row['CYCLE_START_DATE' if which == 'start' else 'CYCLE_END_DATE']).strip(),
                '%m/%d/%Y'
            ).date()
            if cycle_date == input_date:
                return row['CYCLE_ID']
        except Exception:
            continue

    raise ValueError(f"No matching CYCLE_ID for {date_str} ({input_date})")

def split_cycle_range(cycle_range: str) -> tuple[str, str]:
    """
    Splits a cycle range string into start and end dates.
    """
    cycle_range = cycle_range.strip()
    # Case A – ISO yyyy-mm-dd – yyyy-mm-dd  (extra spaces optional)
    iso = re.match(
        r'^([0-9]{4}-[0-9]{2}-[0-9]{2})\s*-\s*([0-9]{4}-[0-9]{2}-[0-9]{2})$',
        cycle_range,
    )
    if iso:
        return iso.group(1), iso.group(2)
    # Case B – “Month YYYY – Month YYYY”
    words = re.match(
        r'^([A-Za-z]{3,9}\s+[0-9]{4})\s*-\s*([A-Za-z]{3,9}\s+[0-9]{4})$',
        cycle_range,
    )
    if words:
        return words.group(1), words.group(2)
    raise ValueError(f'Could not parse cycle range: {cycle_range}')
    
def parse_list(raw):
    """Convert a comma-separated string into a stripped list."""
    return [item.strip() for item in raw.split(",")] if raw else []

def get_int_value(data, key):
    """Get an integer value from data by key, or None if missing."""
    val = get_value(data, key)
    return int(val) if val is not None else None

def get_time_ids(data, df_time):
    """Extract start time IDs for OCCP and reference cycles."""
    cycle_range = get_value(data, "OCCP Cycle Length")
    ref_cycle_range = get_value(data, "Reference Cycle")
    cycle_start, _ = split_cycle_range(cycle_range)
    ref_cycle_start, _ = split_cycle_range(ref_cycle_range)
    return (
        get_time_id(cycle_start, df_time, which='start'),
        get_time_id(ref_cycle_start, df_time, which='start')
    )

def build_hcp_constraints_rows(
    envelope_matrix_df, econsent, brand_ids, sales_line, occp_type, df_sales_line, df_channel, df_master,
    next_id, cycle_start_id, ref_cycle_start_id, ETL_INSERT
):
    """Build rows for HCP constraints DataFrame."""
    rows = []
    for idx, row in envelope_matrix_df.iterrows():
        channel_name = row['CHANNEL']
        mapped_channel = map_channels_with_consent([channel_name], econsent)[0]
        channel_id = get_channel_id(mapped_channel, df_channel)
        ref_cycle_actual = row['SEGMENT'] if envelope_matrix_df.columns[2] == 'SEGMENT' else row['REFERENCE_CYCLE_ACTUAL']
        for brand_id in brand_ids:
            sales_table_id = get_sales_table_id(sales_line, brand_id, occp_type, df_sales_line)
            fact_id = get_fact_id(sales_table_id, channel_id, df_master)
            rows.append({
                'ID': next_id,
                'FACT_ID': fact_id,
                'UPCOMING_TIME_ID': cycle_start_id,
                'REFERENCE_TIME_ID': ref_cycle_start_id,
                'REF_CYCLE_ACTUAL': ref_cycle_actual,
                'MIN_VAL': row['MIN_VALUE'],
                'MAX_VAL': row['MAX_VALUE'],
                'ETL_LOAD_ID': 'LOAD_' + datetime.now().strftime('%Y%m%d'),
                'ETL_INSERT': ETL_INSERT,
                'ETL_UPDATE': None,
                'MOST_RECENT_FLAG': 'Y'
            })
    return rows

def create_business_constraints_file(
    data, sales_line, envelope_matrix_df,
    df_channel, df_sales_line, df_master, df_brand, df_time, conn
):
    """DS Business Constraints"""

    starting_id = get_latest_id_from_snowflake("DS_BUSINESS_CONSTRAINTS", conn)
    next_id = f"C_{starting_id:07d}"

    brands = parse_list(get_value(data, "OCCP Brand"))
    channels = parse_list(get_value(data, "OCCP Channels"))
    econsent = str(get_value(data, "e-consent")).strip().lower() in ["true", "yes", "y"]

    cycle_start_id, ref_cycle_start_id = get_time_ids(data, df_time)

    mapped_channels = map_channels_with_consent(channels, econsent)
    brand_ids = [get_brand_id(b, df_brand) for b in brands]
    channel_ids = [get_channel_id(ch, df_channel) for ch in mapped_channels]

    upcoming_working_days = get_int_value(data, "Number of Working Days for Upcoming cycle")
    reference_working_days = get_int_value(data, "Number of Working Days for Reference cycle")

    ETL_INSERT = pd.to_datetime(datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    occp_type = get_value(data, "Monobrand/Multibrand OCCP")

    # Business constraints
    business_constraints_rows = []
    for brand_id in brand_ids:
        sales_table_id = get_sales_table_id(sales_line, brand_id, occp_type, df_sales_line)
        for channel, mapped_channel, channel_id in zip(channels, mapped_channels, channel_ids):
            fact_id = get_fact_id(sales_table_id, channel_id, df_master)
            avg_rep_capacity = get_avg_rep_capacity(data, channel)
            business_constraints_rows.append({
                'ID': next_id,
                'FACT_ID': fact_id,
                'UPCOMING_TIME_ID': cycle_start_id,
                'REFERENCE_TIME_ID': ref_cycle_start_id,
                'AVG_REP_CAPACITY': avg_rep_capacity,
                'ETL_LOAD_ID': 'LOAD_' + datetime.now().strftime('%Y%m%d'),
                'ETL_INSERT': ETL_INSERT,
                'ETL_UPDATE': None,
                'MOST_RECENT_FLAG': 'Y'
            })

    df_business_constraints = pd.DataFrame(business_constraints_rows)

    # Brand specific constraints
    brand_distribution_map = parse_brand_distribution(str(get_value(data, "Brand distribution")))
    specialties = get_specialty(data, brands)
    file_format = "VEEVA" if get_value(data, "Veeva Align format") == "Yes" else "None"

    brand_specific_rows = []
    if len(brands) > 1:
        for brand, brand_id in zip(brands, brand_ids):
            percent = brand_distribution_map.get(brand.upper(), "")
            brand_specific_rows.append({
                'BRAND_ID': brand_id,
                'BRAND_DISTRIBUTION': percent,
                'SPECIALTIES': specialties,
                'FILE_FORMAT': file_format,
                'ETL_LOAD_ID': 'LOAD_' + datetime.now().strftime('%Y%m%d'),
                'ETL_INSERT': ETL_INSERT,
                'ETL_UPDATE': None,
                'MOST_RECENT_FLAG': 'Y'
            })

    df_brand_specific = pd.DataFrame(brand_specific_rows) if brand_specific_rows else None

    # HCP constraints
    hcp_constraints_rows = build_hcp_constraints_rows(
        envelope_matrix_df, econsent, brand_ids, sales_line, occp_type, df_sales_line, df_channel, df_master,
        next_id, cycle_start_id, ref_cycle_start_id, ETL_INSERT
    )
    df_hcp_constraints = pd.DataFrame(hcp_constraints_rows)

    return df_business_constraints, df_brand_specific, df_hcp_constraints



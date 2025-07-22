"""Rep Utilization Calculations

This module provides functionality to calculate the rep utilization and
automate the process in our web tool.
"""
from typing import List, Dict, Any
import pandas as pd
from streamlit import session_state as ss

def calculate_cycle_capacity_per_channel(
    session: Any, unique_channels: List[str]
) -> Dict[str, Any]:
    """Calculate channel capacities based on territories and working days."""
    try:
        rep_hcp_data = session.rep_occp_df
        territory_count = rep_hcp_data["TERRITORY_NM"].nunique()
        hcp_count = rep_hcp_data["HCP_ID"].nunique()
        channel_capacity = {channel: territory_count * session.working_days *
                            session.get(f"channel_capacity_{channel}", 0)
                            for channel in unique_channels}
        return {
            'territory_count': territory_count,
            'hcp_count': hcp_count,
            'channel_capacity': channel_capacity
        }
    except Exception as error:
        return {
            'territory_count': 0,
            'hcp_count': 0,
            'channel_capacity': {},
            'error': str(error)
        }

def map_hcp_segments_and_rte_column() -> pd.DataFrame:
    """Merge HCP, segment, and consent data into a single DataFrame."""
    try:
        rep_map_df = ss.rep_occp_df
        hcp_characteristics_brand_df = ss.characterstics_df
        e_consent_df = ss.e_consent_df
        merged_df = pd.merge(
            rep_map_df[['HCP_ID']],
            hcp_characteristics_brand_df[['HCP_ID', 'SEGMENT_BRAND1']],
            on='HCP_ID',
            how='inner'
        )
        merged_df['SEGMENT_ALIAS'] = merged_df['SEGMENT_BRAND1'].apply(
            lambda x: 'Others' if pd.isnull(x) or str(x).strip().lower() == 'none' else x
        )
        merged_df = pd.merge(
            merged_df,
            e_consent_df[['HCP_ID', 'REP_CONSENT_EMAIL']],
            on='HCP_ID',
            how='left'
        )
        return merged_df
    except Exception as error:
        return pd.DataFrame({'error': [str(error)]})

def assign_channel_envelope(
    data_df: pd.DataFrame, channel: str, segments_dict: Dict[str, Any]
) -> pd.DataFrame:
    """Assign lower and upper interaction values for each segment and channel."""
    try:
        for segment, (start, end) in segments_dict.items():
            condition = data_df['SEGMENT_ALIAS'] == segment
            data_df.loc[condition, [f"{channel}_lower", f"{channel}_upper"]] = [start, end]
        return data_df
    except Exception as error:
        data_df['error'] = str(error)
        return data_df

def get_channel_segments_dict(channel: str) -> Dict[str, Any]:
    """Helper to fetch the segment dict for a channel from session state."""
    key = channel.replace(' ', '_')
    return ss.final_hcp_segments_dict.get(key, {})

def channel_utilization_status(session: Any, unique_channels: List[str]) -> Dict[str, Any]:
    """Check channel utilization status and generate summary messages."""
    capacity_dict = calculate_cycle_capacity_per_channel(session, unique_channels)
    merged_df = map_hcp_segments_and_rte_column()
    results = {}
    channel_caps = capacity_dict.get('channel_capacity', {})

    for channel in unique_channels:
        segments_dict = get_channel_segments_dict(channel)
        actual_plan = assign_channel_envelope(merged_df.copy(), channel, segments_dict)
        result = evaluate_channel_capacity(actual_plan, channel, channel_caps.get(channel, 0))
        results[channel.replace(' ', '_')] = result

    session.val_results = results
    return results

def evaluate_channel_capacity(
    df: pd.DataFrame, channel: str, cap: float
) -> Dict[str, Any]:
    """Evaluate and summarize channel capacity utilization."""
    lower_col = f"{channel}_lower"
    upper_col = f"{channel}_upper"
    messages = []

    if lower_col not in df.columns or upper_col not in df.columns:
        return {'error': f"Missing columns for {channel}"}

    if channel == "REP_RTE":
        filtered_df = df[df['REP_CONSENT_EMAIL'].fillna(0).astype(str).isin(['1'])]
    else:
        filtered_df = df.copy()

    lower_sum = filtered_df[lower_col].fillna(0).sum()
    upper_sum = filtered_df[upper_col].fillna(0).sum()

    if cap < lower_sum:
        messages.append(
            "**Overutilized**: The current plan is not feasible, as the rep "
            "does not have sufficient capacity to meet even the minimum required interactions. "
            "This situation may introduce compliance and business risks."
        )

    if lower_sum <= cap < lower_sum * 1.10:
        messages.append(
            "**Capacity at Risk**: Capacity is extremely limited. "
            " Although the minimum requirements are technically met,  "
            "there is less than a 10% buffer to create variation for high segement HCPs."
        )

    if upper_sum <= cap <= upper_sum * 1.10:
        messages.append(
            "**Optimal Capacity**: Capacity is well-aligned with requirements. "
            "The plan accommodates the maximum potential interactions and includes a small buffer (≤10%) for strategic flexibility. "
            " This represents the ideal state."
        )

    if cap > upper_sum * 1.10:
        messages.append(
            "**Underutilized**: The Reps capacity exceeds the maximum potential interactions by more than 10%. "
            "This indicates a significant surplus and presents an opportunity to re-evaluate territory assignments or goals."
        )

    if not messages:
        messages.append(
            "Unknown: Could not determine status due to unexpected values."
        )

    return {
        'capacity': cap,
        'lower_sum': lower_sum,
        'upper_sum': upper_sum,
        'message': messages
    }



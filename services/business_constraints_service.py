"""Business constraints service for calculating and generating constraint summaries."""

import pandas as pd
from typing import Dict, List, Tuple, Any
from core.dto import DTOBundle, ChannelCapacityDTO
from core.utils import ChannelMapper

class BusinessConstraintsService:
    """Service for calculating and generating business constraints."""
    
    def calculate_business_constraints(self, bundle: DTOBundle, final_hcp_bounds: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calculate business constraints and return summary DataFrames.
        
        Args:
            bundle: Complete DTO bundle with all OCCP constraints
            final_hcp_bounds: DataFrame with HCP bounds data
            
        Returns:
            Tuple of (summary_df, envelope_matrix_df)
        """
        # Build summary data
        sales_line = {"Input": f"{bundle.market.sales_line}"}
        constant_features = {
            "Generate OCCP for cycle": f"{bundle.cycle.start} - {bundle.cycle.end}",
        }

        multibrand_flag = "Multibrand" if bundle.market.mode == "Multibrand" else "Monobrand"

        occp_context_features = {
            "OCCP Cycle Length": f"{bundle.cycle.months} months",
            "Number of Working Days for upcoming cycle": f"{bundle.cycle.working_days}",
            "Reference Cycle": f"{bundle.reference.start} - {bundle.reference.end}",
            "OCCP Channels": ", ".join(bundle.capacity.channels),
            "Monobrand/Multibrand OCCP": multibrand_flag,
            "OCCP Brand(s)": ", ".join(bundle.market.brands),
            "For Multibrand OCCP only - CHANNELS": (
                ", ".join(bundle.capacity.channels)
                if multibrand_flag == "Multibrand"
                else ""
            ),
        }

        daily_capacity_channels_dict = {
            f"Avg Rep Capacity per day for {channel}": f"{bundle.capacity.daily_capacity.get(channel, 0.0)}"
            for channel in bundle.capacity.channels
        }

        envelope_matrix_rows = []

        # Process envelope matrix data
        if "REFERENCE_CYCLE_ACTUAL" in final_hcp_bounds.columns:
            for idx, row in final_hcp_bounds.iterrows():
                envelope_matrix_rows.append(
                    {
                        "CHANNEL": row["CHANNEL"],
                        "REFERENCE_CYCLE_ACTUAL": row["REFERENCE_CYCLE_ACTUAL"],
                        "MIN_VALUE": row["MIN_VALUE"],
                        "MAX_VALUE": row["MAX_VALUE"],
                    }
                )
        elif "SEGMENT" in final_hcp_bounds.columns:
            for idx, row in final_hcp_bounds.iterrows():
                envelope_matrix_rows.append(
                    {
                        "CHANNEL": row["CHANNEL"],
                        "BRAND": row["BRAND"],
                        "SEGMENT": row["SEGMENT"],
                        "MIN_VALUE": row["MIN_VALUE"],
                        "MAX_VALUE": row["MAX_VALUE"],
                    }
                )

        additional_comments = {
            "Do you need e-consent to be checked for RTE? (Yes/No)": bundle.capacity.e_consent_rte
        }

        hcp_constraints = {
            "Envelope matrix per HCP by channel": "Please refer to 'Envelope matrix - Input' tab"
        }

        # Build summary DataFrame
        data = [
            ("Type", sales_line),
            ("Cycle", constant_features),
            ("OCCP Context", occp_context_features),
            ("Sales Rep. Constraints", daily_capacity_channels_dict),
            ("HCP Constraints", hcp_constraints),
            ("Additional Constraint", additional_comments),
        ]

        rows = []
        for source, dictionary in data:
            for key, value in dictionary.items():
                rows.append(
                    {
                        "Constraint type": source,
                        "Information": key,
                        "Values": value,
                    }
                )
        df = pd.DataFrame(rows)

        envelope_matrix_df = pd.DataFrame(envelope_matrix_rows)

        return df, envelope_matrix_df
    
    def build_excel_data(self, bundle: DTOBundle) -> List[List[str]]:
        """
        Build data rows for Excel export.
        
        Args:
            bundle: Complete DTO bundle
            
        Returns:
            List of data rows for Excel
        """
        data = [
            ["Cycle", "Generate OCCP for cycle", f"{bundle.cycle.name}"],
            [
                "OCCP Context",
                "OCCP Cycle Length",
                f"{bundle.cycle.start.strftime('%b %Y')} - {bundle.cycle.end.strftime('%b %Y')}",
            ],
            [
                "OCCP Context",
                "Number of Working Days for Upcoming cycle",
                f"{bundle.cycle.working_days}",
            ],
            [
                "OCCP Context",
                "Reference Cycle",
                f"{bundle.reference.start.strftime('%b %Y')} - {bundle.reference.end.strftime('%b %Y')}",
            ],
            [
                "OCCP Context",
                "Number of Working Days for Reference cycle",
                f"{bundle.reference.working_days}",
            ],
            [
                "OCCP Context",
                "Monobrand/Multibrand OCCP",
                "Multibrand" if bundle.market.mode == "Multibrand" else "Monobrand",
            ],
            ["OCCP Context", "OCCP Brand(s)", ", ".join(bundle.market.brands)],
            ["OCCP Context", "OCCP Channels", ", ".join(bundle.capacity.channels)],
        ]
        
        if bundle.market.mode == "Multibrand":
            data.append(
                [
                    "For Multibrand OCCP only:",
                    "Select which channels can be multibrand interactions?",
                    ", ".join(bundle.capacity.multibrand_channels),
                ]
            )
            if bundle.market.specialties:
                specialties_str = ", ".join(
                    [
                        f"{brand_str} : {specialty}"
                        for brand_str, specialty in bundle.market.specialties.items()
                    ]
                )
                data.append(
                    [
                        "For Multibrand OCCP only:",
                        "Specify Specialities that can be promoted together ?",
                        specialties_str,
                    ]
                )
            if bundle.distribution:
                brand_distribution_str = ", ".join(
                    [f"{bundle.distribution.ratios[brand]}% {brand}" for brand in bundle.market.brands]
                )
                data.append(
                    [
                        "For Multibrand OCCP only:",
                        "Brand distribution",
                        brand_distribution_str,
                    ]
                )
        
        data.append(
            [
                "Sales Rep. constraints",
                "Avg Rep Capacity for All Channels",
                "{:.2f}".format(
                    sum(
                        bundle.capacity.daily_capacity.get(channel, 0.0)
                        for channel in bundle.capacity.channels
                    )
                ),
            ]
        )
        
        for channel in bundle.capacity.channels:
            if bundle.capacity.non_prescriber_included:
                data.append(
                    [
                        "Sales Rep. constraints",
                        f"Avg Rep Capacity per day for {channel} (Prescriber and Non-Prescriber Combined)",
                        f"{bundle.capacity.daily_capacity.get(channel, 0.0):.2f}",
                    ]
                )
            else:
                data.append(
                    [
                        "Sales Rep. constraints",
                        f"Avg Rep Capacity per day for {channel}",
                        f"{bundle.capacity.daily_capacity.get(channel, 0.0):.2f}",
                    ]
                )

        # Add RTE consent if applicable
        if any(
            _channel in bundle.capacity.channels for _channel in ["RTE-Open", "RTE-Sent"]
        ):
            consent_flag = "Yes" if bundle.capacity.e_consent_rte else "No"
            data.append(
                [
                    "Additional Constraints",
                    "eConsent required for RTE?",
                    consent_flag,
                ]
            )

        return data 

    @staticmethod
    def validate_brand_distribution(ratios: dict) -> None:
        """
        Validate that brand distribution ratios are non-negative and sum to 100.
        Raises ValueError if invalid.
        """
        if any(v < 0 or v > 100 for v in ratios.values()):
            raise ValueError("Each brand ratio must be between 0 and 100.")
        if sum(ratios.values()) != 100:
            raise ValueError("Brand ratios must sum to 100%.")

    @staticmethod
    def validate_envelope_matrix(envelopes: list) -> None:
        """
        Validate that for each envelope, min_val <= max_val and all values are >= 0.
        Raises ValueError if invalid.
        """
        for env in envelopes:
            min_val = getattr(env.rule, 'min_val', None)
            max_val = getattr(env.rule, 'max_val', None)
            if min_val is not None and max_val is not None:
                if min_val < 0 or max_val < 0:
                    raise ValueError("Envelope min/max values must be >= 0.")
                if max_val < min_val:
                    raise ValueError(f"Envelope max_val ({max_val}) must be >= min_val ({min_val}).")

    @staticmethod
    def validate_channel_capacity(daily_capacity: dict) -> None:
        """
        Validate that all channel capacities are >= 0.
        Raises ValueError if invalid.
        """
        for channel, value in daily_capacity.items():
            if value < 0:
                raise ValueError(f"Channel capacity for {channel} must be >= 0.") 
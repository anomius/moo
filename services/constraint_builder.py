"""Constraint builder service for transforming DTOs into OCCP payload."""

from typing import Dict, List, Any
from core.dto import DTOBundle
from core.utils import ChannelMapper, MonthPlanner, BrandCombinator, CountryCodeMapper

class ConstraintBuilder:
    """Builds OCCP payload from DTO bundle."""
    
    def build(self, bundle: DTOBundle) -> Dict[str, Any]:
        """
        Build OCCP payload from DTO bundle.
        
        Args:
            bundle: Complete DTO bundle with all OCCP constraints
            
        Returns:
            Dictionary containing the OCCP payload
        """
        # Build interaction channels
        interaction_channels, combined_interactions_dict, channel_rep_col = self._build_interaction_channels(bundle)
        
        # Build constraints
        constraints = self._build_constraints(bundle, interaction_channels, combined_interactions_dict)
        
        # Get months
        months_to_optimize, actual_months = self._get_months(bundle)
        
        # Build feature list
        feat_lst = interaction_channels + self._default_features()
        channel_cols_all = interaction_channels + channel_rep_col
        
        # Get country code
        selected_country_code = CountryCodeMapper.get_code(bundle.market.country.upper())
        multi_brand_sel = bundle.market.mode != "Monobrand"
        
        # Build capacity constraints
        capacity_constraints = self._build_capacity_constraints(bundle, channel_rep_col)
        
        # Build result
        result = {
            "country_code": selected_country_code,
            "country": bundle.market.country.upper(),
            "brand": bundle.market.brands,
            "all_channel_cols": interaction_channels,
            "interaction_channels": interaction_channels,
            "channel_cols": interaction_channels,
            "channel_cols_all": channel_cols_all,
            "feature_list": feat_lst,
            "multibrand_data": multi_brand_sel,
            "max_country": True,
            "occp_length": bundle.cycle.months,
            "months_to_optimize": months_to_optimize,
            "actual_date_range": actual_months,
            "CYCLE_NAME": bundle.cycle.name.replace(" ", "_"),
            "CYCLE_START_DATE": str(bundle.cycle.start),
            "CYCLE_END_DATE": str(bundle.cycle.end),
            "e_consent": bundle.capacity.e_consent_rte,
            "combined_interactions_dict": combined_interactions_dict,
            "n_months": len(months_to_optimize),
            "channel_brand_dict": combined_interactions_dict,
            "capacity_constraints": capacity_constraints,
            "constraints": constraints,
            "is_non_prescriber": bundle.capacity.non_prescriber_included,
            "non_prescribers_priority": bundle.capacity.non_prescriber_priority,
        }
        
        # Add non-prescriber constraints if present
        if bundle.non_prescriber:
            non_prescribers_bounds = self._build_non_prescriber_constraints(bundle)
            result["NON_PRESCRIBERS_ENVELOPE_RULES"] = non_prescribers_bounds
        
        return result
    
    def _build_interaction_channels(self, bundle: DTOBundle):
        """Build interaction channels and related dictionaries."""
        interaction_channels = []
        combined_interactions_dict = {}
        channel_rep_col = []
        
        # Create brand mapping
        brand_map = {brand: f'BRAND{i+1}' for i, brand in enumerate(bundle.market.brands)}
        
        for channel in bundle.capacity.channels:
            channel_upper = channel.upper()
            mapped_channel = ChannelMapper.canonical(channel_upper).replace(" ", "_")
            channel_key = f"REP_{mapped_channel}"
            channel_rep_col.append(channel_key)
            combined_interactions_dict[channel_key] = []
            
            # Add monobrand interactions
            for brand in bundle.market.brands:
                if brand in brand_map:
                    interaction = f"{channel_key}_{brand_map[brand]}"
                    interaction_channels.append(interaction)
                    combined_interactions_dict[channel_key].append(interaction)
            
            # Add multibrand interactions if applicable
            if any(channel.lower() == ch.lower() for ch in bundle.capacity.multibrand_channels):
                for combo in BrandCombinator.get_combinations(bundle.market.brands):
                    if all(b in brand_map for b in combo):
                        combo_key = "_AND_".join([brand_map[b] for b in combo])
                        interaction = f"{channel_key}_{combo_key}"
                        interaction_channels.append(interaction)
                        combined_interactions_dict[channel_key].append(interaction)
        
        return interaction_channels, combined_interactions_dict, channel_rep_col
    
    def _build_constraints(self, bundle: DTOBundle, interaction_channels, combined_interactions_dict):
        """Build constraints dictionary."""
        if bundle.uses_segment_matrix:
            return {
                "ENVELOPE_RULES": self._transform_hcp_segments(bundle.envelopes_seg)
            }
        else:
            return {
                "ENVELOPE_RULES": self._transform_hcp_bounds(bundle.envelopes_hist, interaction_channels)
            }
    
    def _transform_hcp_bounds(self, hcp_bounds, interaction_channels):
        """Transform HCP bounds for output config."""
        # This is a simplified version - the actual implementation would need
        # to handle all the transformation logic from the original ui.py
        return {}
    
    def _transform_hcp_segments(self, hcp_segments):
        """Transform HCP segments for output config."""
        # This is a simplified version - the actual implementation would need
        # to handle all the transformation logic from the original ui.py
        return {}
    
    def _build_non_prescriber_constraints(self, bundle: DTOBundle):
        """Build non-prescriber constraints."""
        non_prescribers_bounds = {}
        for envelope in bundle.non_prescriber:
            channel_key = f"REP_{ChannelMapper.canonical(envelope.channel)}"
            non_prescribers_bounds[channel_key] = [envelope.rule.min_val, envelope.rule.max_val]
        return non_prescribers_bounds
    
    def _get_months(self, bundle: DTOBundle):
        """Get months to optimize and actual months."""
        months_to_optimize = MonthPlanner.get_months_to_optimize(
            bundle.cycle.start, bundle.cycle.months
        )
        actual_months = MonthPlanner.get_actual_months(
            bundle.reference.start, bundle.reference.months
        )
        return months_to_optimize, actual_months
    
    def _default_features(self):
        """Get default features list."""
        return [
            "MONTH_1", "MONTH_2", "MONTH_3", "MONTH_4", "MONTH_5", "MONTH_6",
            "MONTH_7", "MONTH_8", "MONTH_9", "MONTH_10", "MONTH_11",
            "BRICK_SALES_AMOUNT_MA_3",
        ]
    
    def _build_capacity_constraints(self, bundle: DTOBundle, channel_rep_col):
        """Build capacity constraints."""
        daily_capacity_channels_dict = {}
        
        for rep_channel in channel_rep_col:
            canonical = rep_channel.replace("REP_", "").upper()
            raw_label = ChannelMapper.canonical(canonical)
            key = f"channel_capacity_{raw_label}"
            
            # Find the corresponding channel in the capacity DTO
            for channel, capacity in bundle.capacity.daily_capacity.items():
                if ChannelMapper.canonical(channel) == raw_label:
                    value = capacity
                    break
            else:
                value = 0.0
            
            daily_capacity_channels_dict[rep_channel] = int(
                (value * bundle.cycle.working_days) / bundle.cycle.months
            )
        
        return {bundle.market.sales_line: daily_capacity_channels_dict} 
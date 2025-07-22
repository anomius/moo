"""Utils

This module provides deep_merge utility to be used for merging
configs for OCCP cycles.
"""
import os
import copy
from typing import Any, List, Tuple, Union, Iterable
from collections.abc import Mapping, Sequence

from turing_generic_lib.utils.snowflake_connection import (
    prepare_snowflake_params,
    snowflake_connector,
)

import yaml

ENV = os.environ.get("ENVIRONMENT", "DEV")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
config_map_path = os.path.join(CONFIG_DIR, "config_mapping.yaml")
brand_mapping_path = os.path.join(CONFIG_DIR, "brand_mapping.yaml")
brand_name_path = os.path.join(CONFIG_DIR, "brand_name_mapping.yaml")

with open(brand_mapping_path, "r") as file:
    brand_map = yaml.safe_load(file)["BRAND"]
with open(brand_name_path, "r") as file:
    brand_name_map = yaml.safe_load(file)["NAME_MAP"]

with open(config_map_path, "r") as file:
    config_map = yaml.safe_load(file)


def get_brand_code(brand):
    """Load the brand mapping from the YAML file"""

    brand_code = None
    for code, name in brand_map.items():
        if name == brand:
            brand_code = code
            break
    if brand_code is None:
        brand_code = brand

    return brand_code


def merge_yaml(yaml_str, multi_brands_sel):
    """This function is for testing in Dev environment only"""
    # Define the output file path from yaml_str cr and product name
    try:
        # Parse the YAML string
        data = yaml.safe_load(yaml_str)

        # Extract values with error handling
        country_code = data.get("country_code", "err")
        brands = data.get("brand", ["err"])

        # set brands to the mapped value in data

        # Ensure brands is treated as a list and get the first element for single brand
        if isinstance(brands, list) and len(brands) > 0:
            if len(brands) > 1 and not multi_brands_sel:

                return None
            elif len(brands) > 1 and multi_brands_sel:
                brands_code = [get_brand_code(b) for b in brands]
            elif len(brands) == 1:
                brand = brands[0]
                brand_code = get_brand_code(brand)
        else:

            return None

        if multi_brands_sel == True:
            # Join the brand codes with a separator
            brands_path = "_".join(brands_code)
            output_dir = os.path.join(
                "./config", "gen", country_code, brands_path, "BRICK"
            )
        else:
            brand_path = brand_code
            output_dir = os.path.join(
                "./config", "gen", country_code, brand_path, "BRICK"
            )

        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        output_yaml = os.path.join(output_dir, "config.yaml")
 

        if os.path.exists(output_yaml):
            # Load the existing YAML file
            with open(output_yaml, "r") as file:
                base_cfg = yaml.safe_load(file)
        else:
            base_cfg = {}

        merged_cfg = deep_merge_configs(base_cfg, data)

        yaml_str = yaml.dump(merged_cfg, sort_keys=False, indent=2)
    
        with open(output_yaml, "w") as f:
            f.write(yaml_str)

        return output_yaml
    except yaml.YAMLError:

        return None


# This function will change the value at the specified path in the dictionary.
def set_value_at_path(dictionary: dict, path: str, value: Any) -> None:
    """Set value at specified path in dictionary."""
    keys = path.split(".")
    for key in keys[:-1]:
        dictionary = dictionary.setdefault(key, {})
    dictionary[keys[-1]] = value


# This function will retrieve the value at the specified path in the dictionary.
def get_value_at_path(dictionary: dict, path: str) -> Any:
    """Get value at specified path in dictionary."""
    keys = path.split(".")
    for key in keys:
        dictionary = dictionary.get(key, {})
        if dictionary is None:
            return None
    return dictionary


def keys_equal(key1: str, key2: str, case_insensitive: bool = False) -> bool:
    """Check if keys are equal, optionally case insensitive."""
    return key1.lower() == key2.lower() if case_insensitive else key1 == key2


def find_key(
    mapping: Mapping[str, Any], key: str, case_insensitive: bool = False
) -> Union[str, None]:
    """Find the physical key in mapping matching the given key."""
    if not case_insensitive:
        return key if key in mapping else None
    lk = key.lower()
    return next((k for k in mapping if k.lower() == lk), None)


def collect_leaf_updates(
    path: List[str], node: Any
) -> list[Tuple[List[str], Any]]:
    """Collect all leaf updates from a nested structure."""
    if isinstance(node, Mapping):
        updates: list[Tuple[List[str], Any]] = []
        for k, v in node.items():
            updates.extend(collect_leaf_updates(path + [k], v))
        return updates
    return [(path, node)]


def update_matching_keys(
    node: Mapping, key: str, tail: List[str], value: Any, case_insensitive: bool
) -> None:
    """
    Update all matching keys at the current depth of the mapping.

    If tail is not empty, recursively update deeper paths; otherwise, update the value.

    Args:
        node: The mapping (dictionary-like object) to update.
        key: The current key to match.
        tail: Remaining path as a list of keys.
        value: The value to set at the leaf.
        case_insensitive: Whether to match keys case-insensitively.
    """
    for k in list(node.keys()):
        if keys_equal(k, key, case_insensitive):
            if tail:
                propagate_leaf_updates(node[k], tail, value, case_insensitive)
            else:
                node[k] = value


def search_deeper(
    item: Any, path: List[str], value: Any, case_insensitive: bool
) -> None:
    """
    Recursively search for mappings within nested structures and propagate updates.

    Args:
        item: The current item to inspect (can be Mapping, Sequence, etc.).
        path: The path to propagate as a list of keys.
        value: The value to set at the leaf.
        case_insensitive: Whether to match keys case-insensitively.
    """
    if isinstance(item, Mapping):
        propagate_leaf_updates(item, path, value, case_insensitive)
    elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
        for subitem in item:
            if isinstance(subitem, Mapping):
                propagate_leaf_updates(subitem, path, value, case_insensitive)


def propagate_leaf_updates(
    node: Any, path: List[str], value: Any, case_insensitive: bool
) -> None:
    """
    Propagate leaf updates to all matching paths in a nested structure.

    Args:
        node: The root node to start updating from.
        path: The path to propagate as a list of keys.
        value: The value to set at the leaf.
        case_insensitive: Whether to match keys case-insensitively.
    """
    if not path or not isinstance(node, Mapping):
        return

    head, *tail = path
    update_matching_keys(node, head, tail, value, case_insensitive)

    for val in node.values():
        search_deeper(val, path, value, case_insensitive)


def _leaves(path: List[str], node: Any, norm) -> Iterable[Tuple[List[str], Any]]:
    """Yield (path, value) for every non-mapping leaf under node."""
    if isinstance(node, Mapping):
        for key, val in node.items():
            yield from _leaves(path + [norm(key)], val, norm)
    else:
        yield (path, node)

def propagate_in_sequence(seq, path, value, norm):
    """
    Recursively applies _propagate to each mapping element in a sequence.

    Args:
        seq: A sequence (list or tuple) potentially containing mapping elements.
        path: The path to propagate.
        value: The value to set at each matching path.
        norm: The normalization function for keys.

    Returns:
        None. The function applies _propagate in place to each mapping in the sequence.
    """
    for item in seq:
        if isinstance(item, Mapping):
            _propagate(item, path, value, norm)

def _propagate(node: Any, path: list[str], value: Any, norm) -> None:
    """
    Recursively copy a value to every occurrence of a given path within a nested mapping.

    For each occurrence of the specified path under the mapping `node`, this function sets
    the value at that path to a deep copy of `value`. The function traverses nested mappings
    and sequences (lists/tuples), applying the update wherever the path matches.

    Args:
        node: The root mapping (dict-like object) to traverse and update.
        path: A list of normalized keys representing the path to update.
        value: The value to set at each matching path (deep-copied).
        norm: A normalization function applied to keys (e.g., for case-insensitivity).

    Returns:
        None. The function updates `node` in place.
    """
    if not path or not isinstance(node, Mapping):
        return

    head, *tail = path

    for key, val in node.items():
        key_norm = norm(key)
        if key_norm == head:
            if not tail:
                node[key] = copy.deepcopy(value)
                continue
            _propagate(val, tail, value, norm)
        if isinstance(val, Mapping):
            _propagate(val, path, value, norm)
        if isinstance(val, (list, tuple)) and not isinstance(val, (str, bytes)):
            propagate_in_sequence(val, path, value, norm)

def _merge(dst: dict, src: Mapping, cur: List[str], pending: list, norm) -> None:
    """Merge src into dst and collect leaf updates."""
    for k_src, v_src in src.items():
        k_norm = norm(k_src)
        k_dst = next((k for k in dst if norm(k) == k_norm), str(k_src))
        if isinstance(v_src, Mapping) and isinstance(dst.get(k_dst), Mapping):
            _merge(dst[k_dst], v_src, cur + [k_norm], pending, norm)
        else:
            dst[k_dst] = copy.deepcopy(v_src)
    pending.extend(_leaves(cur, src, norm))

def deep_merge_configs(
    base: Mapping[str, Any],
    incoming: Mapping[str, Any],
    *,
    case_insensitive: bool = False,
) -> dict[str, Any]:
    """
    Merge two nested mappings (dictionaries) with advanced rules:
    1. Merge *incoming* into *base*: scalars/sequences overwrite, nested dicts merge key-by-key.
    2. For every leaf updated in *incoming*, replicate the same (path, value) everywhere that path already exists in *base*.
    3. Apply ``config_map``: copy the value found at each *source* path in *incoming* onto the corresponding *dest* path in the result.
    """
    norm = (lambda k: str(k).lower()) if case_insensitive else (lambda k: str(k))
    result: dict[str, Any] = copy.deepcopy(base)
    pending: list[Tuple[List[str], Any]] = []
    _merge(result, incoming, [], pending, norm)
    for path, val in pending:
        _propagate(result, path, val, norm)
    for dest_path, src_path in config_map.items():
        val = get_value_at_path(incoming, src_path)
        if val is not None:
            set_value_at_path(result, dest_path, val)
    return result

class SnowflakeConnection:
    """Singleton for Snowflake connection."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Create or reuse singleton instance."""
        if cls._instance is None:
            cls._instance = super(SnowflakeConnection, cls).__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, config):
        """Initialize with config."""
        self.config = config
        self.set_snowflake_conn()

    def set_snowflake_conn(self):
        """Set up Snowflake connection."""
        region = "EMEA"
        snowflake_params_all = self.config.snowflake_config["SNOWFLAKE"][region][ENV]
        self.snowflake_params = prepare_snowflake_params(
            snowflake_params_all, "SCHEMA_NBA"
        )
        self.output_snowflake_params = prepare_snowflake_params(
            snowflake_params_all, "SCHEMA_DS"
        )
        self.snowflake_con = snowflake_connector(self.snowflake_params)
        self.output_snowflake_con = snowflake_connector(self.output_snowflake_params)

    def get_connection(self):
        """Return Snowflake connection."""
        return self.snowflake_con, self.output_snowflake_con



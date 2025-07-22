from infra.snowflake_repo import SnowflakeRepo
from turing_generic_lib.utils.config import TuringConfig
from typing import List, Optional
import datetime

class UIDataService:
    _repo = None

    @classmethod
    def _get_repo(cls):
        if cls._repo is None:
            # You may want to make config dynamic or pass it in
            config = TuringConfig(
                config_dir=None,  # Set as needed
                gbu="gen",
                countrycode="IT",
                brand="TOJ",
            )
            config.load()
            cls._repo = SnowflakeRepo(config)
        return cls._repo

    @classmethod
    def get_countries(cls) -> List[str]:
        df_team, _ = cls._get_repo().fetch_team_data()
        return sorted(df_team["COUNTRY"].dropna().unique())

    @classmethod
    def get_sales_lines_for_country(cls, country: str) -> List[str]:
        df_team, _ = cls._get_repo().fetch_team_data()
        return sorted(df_team[df_team["COUNTRY"] == country]["SALES_TEAM"].dropna().unique())

    @classmethod
    def get_brands(cls) -> List[str]:
        _, df_brand = cls._get_repo().fetch_team_data()
        return sorted(df_brand["GLOBAL_BRAND"].dropna().unique())

    @classmethod
    def get_channels(cls) -> List[str]:
        df_channel = cls._get_repo().fetch_channel_data()
        return sorted(df_channel["CHANNEL"].dropna().unique())

    @classmethod
    def get_brand_indications(cls, brand: str) -> List[str]:
        _, df_brand = cls._get_repo().fetch_team_data()
        if "INDICATION_NAME" in df_brand.columns:
            return sorted(df_brand[df_brand["GLOBAL_BRAND"] == brand]["INDICATION_NAME"].dropna().unique())
        return []

    @classmethod
    def get_brand_list_with_indications(cls) -> List[str]:
        _, df_brand = cls._get_repo().fetch_team_data()
        if "INDICATION_NAME" in df_brand.columns:
            dupi_indication = [
                f"DUPIXENT {indi}"
                for indi in df_brand[df_brand["GLOBAL_BRAND"] == "DUPIXENT"]["INDICATION_NAME"].dropna().unique()
            ]
            brand_list = [b for b in df_brand["GLOBAL_BRAND"].dropna().unique() if b != "DUPIXENT"]
            return sorted(list(brand_list) + dupi_indication)
        return sorted(df_brand["GLOBAL_BRAND"].dropna().unique())

    @classmethod
    def get_master_and_time_dim_data(cls):
        return cls._get_repo().fetch_master_and_time_dim_data()

    @classmethod
    def get_validate_data(cls, brand_map: List[str], cycle_start_date: datetime.date, country: str):
        return cls._get_repo().fetch_validate_data(brand_map, cycle_start_date, country) 
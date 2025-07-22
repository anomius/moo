import pandas as pd
import os
from utils.utils import SnowflakeConnection

class SnowflakeRepo:
    def __init__(self, config):
        # Use the singleton SnowflakeConnection from utils.utils
        self.snowflake_con, _ = SnowflakeConnection(config).get_connection()
        self.sql_dir = os.path.join(os.path.dirname(__file__), "../sql")

    def _open_sql_file(self, filename):
        with open(os.path.join(self.sql_dir, filename), "r", encoding="utf-8") as f:
            return f.read()

    def fetch_team_data(self):
        """Fetch team and brand data from Snowflake."""
        team_query = self._open_sql_file("country_sales_line.sql")
        brand_query = self._open_sql_file("gbu_brand.sql")
        df_team = pd.read_sql(team_query, self.snowflake_con)
        df_team.dropna(subset=["COUNTRY", "SALES_TEAM"], inplace=True)
        df_brand = pd.read_sql(brand_query, self.snowflake_con)
        df_brand.dropna(subset=["GLOBAL_BRAND"], inplace=True)
        return df_team, df_brand

    def fetch_channel_data(self):
        """Fetch channel data from Snowflake."""
        channel_query = self._open_sql_file("channel.sql")
        df_channel = pd.read_sql(channel_query, self.snowflake_con)
        df_channel.dropna(subset=["CHANNEL"], inplace=True)
        return df_channel

    def fetch_master_and_time_dim_data(self):
        """Fetch master and time dimension data from Snowflake."""
        master_query = self._open_sql_file("master_data.sql")
        time_dim_query = self._open_sql_file("time_dimension.sql")
        df_master = pd.read_sql(master_query, self.snowflake_con)
        df_time_dim = pd.read_sql(time_dim_query, self.snowflake_con)
        return df_master, df_time_dim

    def fetch_validate_data(self, brand_map, cycle_start_date, country):
        """Fetch e-consent, rep_occp, and HCP characteristics data."""
        e_consent_query = self._open_sql_file("e_consent_characterstics.sql")
        rep_occp_query = self._open_sql_file("rep_occp.sql")
        characterstics_query = self._open_sql_file("characterstics_brand.sql")

        # Replace parameters in queries
        date_format_str = "%Y-%m-%d"
        cycle_end_date = (cycle_start_date - pd.Timedelta(days=1)).strftime(date_format_str)
        e_consent_query = e_consent_query.replace("_COUNTRY_", f"'{country}'").replace("_CYCLE_END_DT_", f"'{cycle_end_date}'")
        rep_occp_query = rep_occp_query.replace("_COUNTRY_", f"'{country}'").replace("_CYCLE_END_DT_", f"'{cycle_end_date}'")

        # Brand replacement logic
        brand_str = ", ".join([f"'{b.strip().upper()}'" for b in brand_map])
        e_consent_query = e_consent_query.replace("_BRAND_", brand_str)
        rep_occp_query = rep_occp_query.replace("_BRAND_", brand_str)

        e_consent_df = pd.read_sql(e_consent_query, self.snowflake_con)
        rep_occp_df = pd.read_sql(rep_occp_query, self.snowflake_con)

        # HCP characteristics for each brand
        hcp_char_df = None
        for brand in brand_map:
            char_query = characterstics_query.replace("_COUNTRY_", f"'{country}'").replace("_CYCLE_END_DT_", f"'{cycle_end_date}'").replace("_BRAND_", f"'{brand.strip().upper()}'")
            char_df = pd.read_sql(char_query, self.snowflake_con)
            if hcp_char_df is None:
                hcp_char_df = char_df
            else:
                hcp_char_df = pd.merge(hcp_char_df, char_df, on=["HCP_ID"], how="left")

        return e_consent_df, rep_occp_df, hcp_char_df 
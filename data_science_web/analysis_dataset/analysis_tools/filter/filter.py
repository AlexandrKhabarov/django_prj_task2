import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FilterDataFrame:

    @staticmethod
    def del_empty_rows(df):
        return df.dropna(inplace=False, axis=0, how="all")

    @staticmethod
    def del_duplicate(df):
        return df.drop_duplicates(keep="first")

    @staticmethod
    def filter_by_direct(df, signal, start_sector, end_sector):
        return df[(start_sector <= df.loc[:, signal]) & (df.loc[:, signal] <= end_sector)]

    @staticmethod
    def filter_by_speed(df, signal, start_sector, end_sector):
        return df[(start_sector <= df.loc[:, signal]) & (df.loc[:, signal] <= end_sector)]

    @staticmethod
    def group_data_frame(df, start_sector, end_sector, step_group, signal):
        bins = np.arange(
            start_sector,
            end_sector + step_group,
            step_group
        )
        labels = bins[:-1] + step_group / 2
        category = pd.cut(
            df.loc[:, signal],
            bins=bins,
            labels=labels,
            right=False
        )
        return df.groupby(category)

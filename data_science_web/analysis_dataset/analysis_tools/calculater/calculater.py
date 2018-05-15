import numpy as np
import logging
from .constants import AD

logger = logging.getLogger()


class DensityCalcDataFrame:

    def calc_density(self, df):
        new_df = df.copy()
        self._calc_density(new_df)
        return new_df

    @staticmethod
    def _calc_density(df):
        df['AD_1'] = (1 / (df.TEMP_1 + AD.K_0)) * \
                     (
                             ((df.BP_1 * AD.P_0) / AD.R_0) -
                             (((df.RH_1 * 0.0000205 * np.exp(0.0631846 * (df.TEMP_1 + AD.K_0))) / AD.P_0) *
                              ((1 / AD.R_0) - (1 / AD.R_W)))
                     )

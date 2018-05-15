import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import logging
import os

logger = logging.getLogger(__name__)


class GraphManager:

    def __init__(self, path):
        self.path = path

    def dot_graph(self, direct, speed, df, gr_df, name):
        ax = df.plot.scatter(
            x=direct,
            y=speed,
            color='DarkGreen',
            label="UnGroupedDataFrame",
        )
        gr_df.plot.scatter(
            x=direct,
            y=speed,
            color="DarkRed",
            label="GroupedDataFrame",
            marker="^",
            ax=ax
        )
        plt.title("Dot Graph")
        plt.grid(True)
        self._save_graph(name)

    def rose_graph(self, df, direct, step, name):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')
        bins = np.arange(0, 360, step)
        category = pd.cut(
            df.loc[:, direct],
            bins=bins,
            labels=bins[:-1] + step*0.5,
            right=False
        )
        group_df = df.groupby(category).count()
        angles = list(map(lambda x: math.radians(x), group_df.index.values.categories))
        ax.plot(
            angles,
            group_df.values,
            color='r',
            linewidth=1
        )
        ax.plot(
            (angles[-1], angles[0]),
            (group_df.values[-1],
             group_df.values[0]),
            color='r',
            linewidth=1
        )
        plt.legend(["wind direction"], loc=1, bbox_to_anchor=(1.35, 1.1))
        plt.title("Rose Graph")
        plt.grid(True)
        self._save_graph(name)

    def hist_graph(self, df, signal, name):
        df.loc[:, signal].plot.hist(
            title="Wind Speed Histogram",
            bins=np.arange(
                df.loc[:, signal].min(),
                df.loc[:, signal].max(),
                1
            )
        )
        plt.xlabel(signal)
        plt.legend([signal], loc=2)
        plt.grid(True)
        self._save_graph(name)

    def density_graph(self, df, name):
        plt.plot(
            pd.to_datetime(df.index),
            df.loc[:, "AD_1"].values
        )
        plt.grid(True)
        plt.title("Air Density vs Daytime")
        self._save_graph(name)

    def _save_graph(self, name):
        path = os.path.join(self.path, name)
        plt.savefig(path)
        logger.info(
            "[success] plot density graph and save it by path: {path}".format(path=path)
            )
        plt.close()

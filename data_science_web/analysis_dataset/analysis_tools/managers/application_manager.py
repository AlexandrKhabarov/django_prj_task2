from ..graphics import GraphManager
from ..calculater import DensityCalcDataFrame
from ..filter import FilterDataFrame
import pandas as pd
import os


class ApplicationManager:

    def __init__(self):
        self.density = DensityCalcDataFrame()
        self.filtration = FilterDataFrame()

    def go(
            self,
            analysis,
            media_root,
    ):
        analysis_folder = os.path.join(media_root, analysis.name)
        if not os.path.exists(analysis_folder):
            os.mkdir(analysis_folder)

        df, grouped_df = self._manipulate_data_frame(analysis)
        self._create_graphic(
            df,
            grouped_df,
            analysis_folder,
            analysis,
        )
        self._write_result(media_root, f"without_grouping_{analysis.name}.csv", df)
        self._write_result(media_root, f"grouping_data_frame_{analysis.name}.csv", grouped_df)

    def _manipulate_data_frame(self, analysis):
        try:
            df = pd.read_csv(analysis.data_set.path, engine="python", sep=None, index_col="Timestamp")
        except FileNotFoundError:
            df = pd.read_csv(analysis.data_set, engine="c", sep=";", index_col="Timestamp")

        df = self.filtration.del_empty_rows(df)
        df = self.filtration.del_duplicate(df)
        df = self.filtration.filter_by_direct(
            df,
            "WD_{}".format(analysis.signal_direction),
            analysis.start_sector_direction,
            analysis.end_sector_direction
        )
        df = self.filtration.filter_by_speed(
            df,
            "WS_{}".format(analysis.signal_speed),
            analysis.start_sector_speed,
            analysis.end_sector_speed
        )
        df = self.density.calc_density(df)

        grouped_df = self.filtration.group_data_frame(
            df,
            analysis.start_sector_direction,
            analysis.end_sector_direction,
            analysis.step_group,
            "WD_{}".format(analysis.signal_direction)
        ).mean()

        return df, grouped_df

    @staticmethod
    def _create_graphic(
            df,
            grouped_df,
            analysis_folder,
            analysis,
    ):
        grp = GraphManager(analysis_folder)

        grp.dot_graph(
            "WD_{}".format(analysis.signal_direction),
            "WS_{}".format(analysis.signal_speed),
            df,
            grouped_df,
            os.path.join(analysis_folder, "dot_{}.png".format(analysis.name))
        )

        grp.rose_graph(
            df,
            "WD_{}".format(analysis.signal_direction),
            analysis.step_group,
            os.path.join(analysis_folder, "rose_{}.png".format(analysis.name))
        )

        grp.hist_graph(
            df,
            "WS_{}".format(analysis.signal_speed),
            os.path.join(analysis_folder, "hist_{}.png".format(analysis.name)),
        )

        grp.density_graph(
            df,
            os.path.join(analysis_folder, "density_{}.png".format(analysis.name)),
        )

    @staticmethod
    def _write_result(media_dir, csv_name, df):
        abs_path = os.path.join(media_dir, csv_name)
        df.to_csv(abs_path)

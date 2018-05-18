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
            result_analysis,
            media_root,
            with_density_dir,
            group_density_dir,
            density_graph_dir,
            hist_graph_dir,
            dot_graphs_dir,
            rose_graphs_dir,
    ):
        df, grouped_df = self._manipulate_data_frame(analysis)
        self._create_graphic(
            df,
            grouped_df,
            media_root,
            analysis,
            result_analysis,
            density_graph_dir,
            hist_graph_dir,
            dot_graphs_dir,
            rose_graphs_dir
        )
        result_analysis.with_density = self._write_result(
            media_root,
            os.path.join(with_density_dir, "{}.csv".format(analysis.name)),
            df
        )
        result_analysis.group_data_frame = self._write_result(
            media_root,
            os.path.join(group_density_dir, "{}.csv".format(analysis.name)),
            grouped_df
        )

    def _manipulate_data_frame(self, analysis):
        df = pd.read_csv(analysis.data_set.path, engine="python", sep=None, index_col="Timestamp")

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
            media_root,
            analysis,
            result_analysis,
            density_graph_dir,
            hist_graph_dir,
            dot_graph_dir,
            rose_graph_dir
    ):
        grp = GraphManager(media_root)

        base_name_dot_graph = os.path.join(dot_graph_dir, "{}.png".format(analysis.name))

        if not os.path.exists(os.path.join(media_root, dot_graph_dir)):
            os.mkdir(os.path.join(media_root, dot_graph_dir))

        grp.dot_graph(
            "WD_{}".format(analysis.signal_direction),
            "WS_{}".format(analysis.signal_speed),
            df,
            grouped_df,
            base_name_dot_graph,
        )

        result_analysis.dot_graph = base_name_dot_graph

        base_name_rose_graph = os.path.join(rose_graph_dir, "{}.png".format(analysis.name))

        if not os.path.exists(os.path.join(media_root, rose_graph_dir)):
            os.mkdir(os.path.join(media_root, rose_graph_dir))

        grp.rose_graph(
            df,
            "WD_{}".format(analysis.signal_direction),
            analysis.step_group,
            base_name_rose_graph
        )
        result_analysis.rose_graph = base_name_rose_graph

        base_name_hist_graph = os.path.join(hist_graph_dir, "{}.png".format(analysis.name))

        if not os.path.exists(os.path.join(media_root, hist_graph_dir)):
            os.mkdir(os.path.join(media_root, hist_graph_dir))

        grp.hist_graph(
            df,
            "WS_{}".format(analysis.signal_speed),
            base_name_hist_graph,
        )
        result_analysis.hist_graph = base_name_hist_graph

        basename_density_graph = os.path.join(density_graph_dir, "{}.png".format(analysis.name))

        if not os.path.exists(os.path.join(media_root, density_graph_dir)):
            os.mkdir(os.path.join(media_root, density_graph_dir))

        grp.density_graph(
            df,
            basename_density_graph
        )
        result_analysis.density_graph = basename_density_graph

    @staticmethod
    def _write_result(media_dir, base_name,  df):
        abs_path = os.path.join(media_dir, base_name)
        if not os.path.exists(os.path.dirname(abs_path)):
            os.mkdir(os.path.dirname(abs_path))
        df.to_csv(abs_path)
        return base_name


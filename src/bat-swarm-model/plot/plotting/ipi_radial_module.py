"""'sound activations in each ipi' radial heat-map (originally ax[1, 0])."""

import sys

import numpy as np

sys.path.append("./src/bat-swarm-model/core/")

from movement_decision.supporting_functions_for_consistency import (
    convert_detected_sounds_into_grids,
    given_parameters_df_return_grid_matrix_zeros,
)
from plotting.base_module import AnimationModule
from plotting.common import plot_grid_matrix_into_radial_time_series
from plotting.convert_heard_sounds_to_matrix import convert_matrix_for_plotting_nicer


class IPIRadialModule(AnimationModule):
    GRID_POS = (1, 0)
    PROJECTION = "polar"

    def setup(self, parameters_df, history, focal_bat, **_):
        ax = self.ax

        grid_data_time_series = [
            frame["bat_ipi_matrix_for_consistency"] for frame in history
        ]
        rows, columns = given_parameters_df_return_grid_matrix_zeros(parameters_df)[1:3]
        spatial_grid_r = rows
        spatial_grid_theta = columns

        new_angular_resolution = convert_matrix_for_plotting_nicer(
            grid_data_time_series[0], rows, columns, 10, focal_bat
        )[1]
        new_grid_data_time_series = np.array(
            [
                convert_matrix_for_plotting_nicer(i, rows, columns, 10, focal_bat)[0]
                for i in grid_data_time_series
            ]
        )

        new_spatial_grid_theta = np.arange(
            -np.pi + new_angular_resolution / 2, np.pi, new_angular_resolution
        )

        self.new_grid_data_time_series = new_grid_data_time_series

        ax.set_title("sound activations in each ipi")
        ax.tick_params("y", rotation=30)

        self.im = plot_grid_matrix_into_radial_time_series(
            new_grid_data_time_series[0, 0],
            spatial_grid_r,
            new_spatial_grid_theta,
            fig_and_ax=(self.fig, ax),
            cmin=0,
            cmax=1,
        )

        return [self.im]

    def init_frame(self):
        return [self.im]

    def update_frame(self, i, frame, context):
        self.im.set_array(self.new_grid_data_time_series[i, 0].T)
        return [self.im]

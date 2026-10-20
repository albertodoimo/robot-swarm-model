import random
import sys
import uuid
from typing import Tuple

import hydra
import matplotlib.pyplot as plt
import numpy as np
import optuna
from omegaconf import DictConfig

sys.path.extend(
    [
        "./src/robot-swarm-model/",
        "./src/robot-swarm-model/core/",
        "./src/robot-swarm-model/plot/",
    ]
)


from scores.collision_scores import compute_collision_counts_and_length
from scores.milling_score import compute_milling
from scores.polarization_score import compute_polarization
from scores.local_polarization_score import compute_local_polarization
from scores.run_all_score_calculations import (
    filter_bat_positions_from_history,
    reformat_history,
)

from plotting.common import stitch_together_history_lists
from simulation.class_simulation import Simulation
from numpy.lib.stride_tricks import sliding_window_view


@hydra.main(
    version_base=None, config_path="../core/config/", config_name="optimization_config"
)
def run_simulation_w_score_calcs(cfg: DictConfig) -> Tuple[float, float]:
    random.seed(cfg.arena.seed)
    np.random.seed(cfg.arena.seed)
    hydra_dir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    output_dir = hydra_dir + "/data/"
    sim = Simulation(cfg, output_dir)
    sim.run()

    bat_positions_raw, parameters_df, *_ = stitch_together_history_lists(output_dir)
    bat_positions, bat_directions = filter_bat_positions_from_history(bat_positions_raw)
    (
        wall_collision,
        bat_bat_collision,
        timeseries_wall_collision,
        timeseries_bat_bat_collision,
    ) = compute_collision_counts_and_length(bat_positions, parameters_df)
    total_collision_rate = (wall_collision + bat_bat_collision) / cfg.arena.SIM_DURATION
    total_collision_rate = total_collision_rate / cfg.arena.NUM_BATS
    if len(bat_positions_raw) < 59000:
        return np.inf, np.inf
    pol_time_series = [
        compute_polarization(bat_direction_frame)
        for bat_direction_frame in bat_directions
    ]
    # milling_time_series = [
    #     compute_milling(bat_direction_frame, bat_positions[i])
    #     for i, bat_direction_frame in enumerate(bat_directions)
    # ]

    # compute_local_polarization returns (score, local_density); keep the score
    local_polarization_list = np.array(
        [
            compute_local_polarization(
                bat_directions_frame,
                bat_positions[i],
                parameters_df,
                0.8,
                "median",
            )[0]
            for i, bat_directions_frame in enumerate(bat_directions)
        ]
    )

    # running median over a trailing 1 s window
    window_avarage = 3.0
    window = int(window_avarage * round(1.0 / parameters_df["TIME_STEP"]))
    running_median_local_polarization = np.median(
        sliding_window_view(local_polarization_list, window), axis=1
    )

    max_pol_of_group = np.max(pol_time_series[1000:])
    # mena_milling_of_group = np.mean(milling_time_series)
    # print(total_collision_rate, max_pol_of_group, mena_milling_of_group)

    print(
        bat_bat_collision / cfg.arena.SIM_DURATION, running_median_local_polarization[0]
    )
    return (
        bat_bat_collision / cfg.arena.SIM_DURATION,
        running_median_local_polarization[0],
    )


if __name__ == "__main__":
    run_simulation_w_score_calcs()

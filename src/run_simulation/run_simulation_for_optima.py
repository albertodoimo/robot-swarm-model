import random
import sys
import uuid
from typing import Tuple

import hydra
import matplotlib.pyplot as plt
import numpy as np
import optuna
from omegaconf import DictConfig

sys.path.extend(["./src/", "./scripts/"])


from scores.collision_scores import compute_collision_counts_and_length
from scores.milling_score import compute_milling
from scores.polarization_score import compute_polarization
from scores.run_all_score_calculations import (
    filter_bat_positions_from_history,
    load_history_dump,
    reformat_history,
)

from simulation.class_simulation import Simulation
from supporting_files.utilities import load_parameters


@hydra.main(
    version_base=None, config_path="../config/", config_name="optimization_config"
)
def run_simulation_w_score_calcs(cfg: DictConfig) -> Tuple[float, float]:
    random.seed(cfg.arena.seed)
    np.random.seed(cfg.arena.seed)
    hydra_dir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    output_dir = hydra_dir + "/data/"
    sim = Simulation(cfg, output_dir)
    sim.run()

    bat_positions_raw = load_history_dump(output_dir)
    bat_positions, bat_directions = filter_bat_positions_from_history(bat_positions_raw)
    parameters_df = load_parameters(output_dir + "/parameters_used.json")
    (
        wall_collision,
        bat_bat_collision,
        timeseries_wall_collision,
        timeseries_bat_bat_collision,
    ) = compute_collision_counts_and_length(bat_positions, parameters_df)
    total_collision_rate = (bat_bat_collision) / cfg.arena.SIM_DURATION
    total_collision_rate = total_collision_rate / cfg.arena.NUM_BATS
    pol_time_series = [
        compute_polarization(bat_direction_frame)
        for bat_direction_frame in bat_directions
    ]
    milling_time_series = [
        compute_milling(bat_direction_frame, bat_positions[i])
        for i, bat_direction_frame in enumerate(bat_directions)
    ]
    max_pol_of_group = np.max(pol_time_series)
    mena_milling_of_group = np.mean(milling_time_series)
    print(total_collision_rate, max_pol_of_group, mena_milling_of_group)

    return total_collision_rate, max_pol_of_group


if __name__ == "__main__":
    run_simulation_w_score_calcs()

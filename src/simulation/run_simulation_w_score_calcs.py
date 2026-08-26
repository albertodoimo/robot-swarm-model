import random
import sys
import uuid
from typing import Tuple

import hydra
import numpy as np
import optuna
from omegaconf import DictConfig

sys.path.extend(["./src/", "./scripts/"])

from plotting.sim_plotter_single_bat_acoustic_field import visualize
from scores.collision_scores import compute_collision_counts_and_length
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

    # unique_id = uuid.uuid4()
    # visualize(
    #     output_dir=output_dir,
    #     save_animation=hydra_dir,
    #     unique_id=unique_id,
    #     resolution=50,
    #     show_sounds=False,
    #     focal_bat=0,
    # )

    bat_positions_raw = load_history_dump(output_dir)
    bat_positions = filter_bat_positions_from_history(bat_positions_raw)
    parameters_df = load_parameters(output_dir + "/parameters_used.json")
    return compute_collision_counts_and_length(bat_positions, parameters_df)


if __name__ == "__main__":
    run_simulation_w_score_calcs()

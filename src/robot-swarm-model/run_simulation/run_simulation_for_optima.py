import random
import sys
import uuid
import os
from pathlib import Path
from typing import Tuple

import hydra
import matplotlib.pyplot as plt
import numpy as np
import optuna
import omegaconf
from omegaconf import DictConfig
from omegaconf import OmegaConf

OmegaConf.register_new_resolver("eval", eval, replace=True)
OmegaConf.register_new_resolver("div", lambda a, b: float(a) / float(b), replace=True)
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from tqdm import tqdm

sys.path.extend(
    [
        "./src/robot-swarm-model/",
        "./src/robot-swarm-model/core/",
        "./src/robot-swarm-model/plot/",
    ]
)

from data_storage.combine_files_post_storage import (
    stitch_together_pickle_history_lists_and_store,
)

from scores.collision_scores import compute_collision_counts_and_length
from scores.milling_score import compute_milling
from scores.polarization_score import compute_polarization
from scores.local_polarization_score import compute_local_polarization
from scores.run_all_score_calculations import (
    filter_bat_positions_from_history,
    reformat_history,
)
from plotting.visualizer import visualize
from scores.run_all_score_calculations import given_history_list_generate_score_files
from simulation.class_simulation import Simulation

from plotting.common import stitch_together_history_lists
from simulation.class_simulation import Simulation
from numpy.lib.stride_tricks import sliding_window_view


@hydra.main(
    version_base=None, config_path="../core/config/", config_name="optimization_config"
)
def run_simulation_w_score_calcs(cfg: DictConfig) -> Tuple[float, float]:
    random.seed(cfg.arena.seed)
    np.random.seed(cfg.arena.seed)
    random.seed(cfg.arena.seed)
    np.random.seed(cfg.arena.seed)

    hydra_job_dir = HydraConfig.get().runtime.output_dir
    hydra_parent_dir = str(Path(hydra_job_dir).parent)
    job_uuid = uuid.uuid4()

    # fail safe for storage
    try:
        hydra_job_num = getattr(HydraConfig.get().job, "num", uuid.uuid4())
    except omegaconf.errors.MissingMandatoryValue:
        hydra_job_num = job_uuid

    OUTPUT_DIR = hydra_job_dir
    # print(OUTPUT_DIR)
    print(cfg)
    # print(hydra_parent_dir)

    sim = Simulation(
        cfg,
        OUTPUT_DIR,
        store_history=True,
        store_data_for_plotting=True,
        termination_criteria="distance",
    )
    sim.run()

    history_list = stitch_together_pickle_history_lists_and_store(
        OUTPUT_DIR,
        hydra_parent_dir + "/data_file_storage/",
        f"job_number_{hydra_job_num}",
    )

    given_history_list_generate_score_files(
        history_list,
        hydra_job_dir,
        job_uuid,
        hydra_job_num,
        range_of_distance_for_local_score=np.arange(0.5, 1.5, 0.5),
    )

    bat_positions_raw, parameters_df, *_ = stitch_together_history_lists(OUTPUT_DIR)
    bat_positions, bat_directions = filter_bat_positions_from_history(bat_positions_raw)
    (
        wall_collision,
        bat_bat_collision,
        timeseries_wall_collision,
        timeseries_bat_bat_collision,
    ) = compute_collision_counts_and_length(bat_positions, parameters_df)
    if len(bat_positions_raw) < 1 / cfg.arena.TIME_STEP * cfg.arena.SIM_DURATION:
        return np.inf, -np.inf
    pol_time_series = [
        compute_polarization(bat_direction_frame)
        for bat_direction_frame in bat_directions
    ]
    # milling_time_series = [
    #     compute_milling(bat_direction_frame, bat_positions[i])
    #     for i, bat_direction_frame in enumerate(bat_directions)
    # ]

    # compute_local_polarization returns (score, local_density); keep the score
    local_polarization_list = [
        compute_local_polarization(
            bat_directions_frame,
            bat_positions[i],
            parameters_df,
            1,
            "median",
        )[0]
        for i, bat_directions_frame in enumerate(bat_directions)
    ]

    local_polarization_steady = local_polarization_list[1000:]

    max_pol_of_group = np.max(pol_time_series[1000:])
    # mena_milling_of_group = np.mean(milling_time_series)
    # print(total_collision_rate, max_pol_of_group, mena_milling_of_group)

    # print(
    #     bat_bat_collision / cfg.arena.SIM_DURATION, running_median_local_polarization[0]
    # )
    # return (
    #     bat_bat_collision / cfg.arena.SIM_DURATION,
    #     running_median_local_polarization[0],
    # )

    collision_score = bat_bat_collision
    print(collision_score, local_polarization_steady)

    for filepath in os.listdir(hydra_job_dir):
        if ".pkl" in filepath:
            os.remove(hydra_job_dir + "/" + filepath)

    return collision_score, np.mean(local_polarization_steady)


if __name__ == "__main__":
    run_simulation_w_score_calcs()

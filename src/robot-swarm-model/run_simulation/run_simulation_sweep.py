import os
import random
import sys
import uuid
from pathlib import Path

import hydra
import numpy as np
import omegaconf
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

# from plotting.sim_plotter_single_bat_acoustic_field import visualize

from scores.combine_files_post_storage import (
    stitch_together_pickle_history_lists_and_store,
)

# from plotting.arena_module import ArenaModule
# from plotting.info_text_module import InfoTextModule
# from plotting.polarization_milling_module import PolarizationMillingModule
# from plotting.sensory_volume_module import SensoryVolumeModule
from plotting.visualizer import visualize
from simulation.class_simulation import Simulation


@hydra.main(version_base=None, config_path="../config/", config_name="config")
def run_simulation(cfg: DictConfig) -> None:
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
    print(OUTPUT_DIR)
    print(cfg)
    print(hydra_parent_dir)

    sim = Simulation(cfg, OUTPUT_DIR, store_history=True)
    sim.run()

    stitch_together_pickle_history_lists_and_store(
        OUTPUT_DIR,
        hydra_parent_dir + "/data_file_storage/",
        f"job_number_{hydra_job_num}",
    )

    # for filepath in os.listdir(hydra_job_dir):
    #     if ".pkl" in filepath and "history_dump" in filepath:
    #         os.remove(hydra_job_dir + "/" + filepath)
    steps = int(np.floor(1.0 / (cfg.arena.FRAME_RATE * cfg.arena.TIME_STEP)))
    print(f"Skipped between video frames = {steps}")
    timestamp = "_".join(hydra_job_dir.split("/")[-2:])  # "2025-04-05_12-34-56"

    visualize(
        output_dir=OUTPUT_DIR,
        save_animation=hydra_parent_dir,
        unique_id=timestamp,
        steps=max(1, steps),
        show_sounds=True,
        focal_bat=0,
        rows=1,
        columns=2,
        modules=[
            "arena",
            # "polarization_milling",
            "info_text",
            # "ipi_radial",
            # "sum_radial",
            # "sensory_volume",
        ],
    )


if __name__ == "__main__":
    run_simulation()

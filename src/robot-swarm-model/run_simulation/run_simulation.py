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
from omegaconf import OmegaConf

OmegaConf.register_new_resolver("eval", eval, replace=True)
OmegaConf.register_new_resolver("div", lambda a, b: float(a) / float(b), replace=True)

from tqdm import tqdm

sys.path.extend(
    [
        "./src/robot-swarm-model/",
        "./src/robot-swarm-model/core/",
        "./src/robot-swarm-model/plot/",
    ]
)

# from plotting.sim_plotter_single_bat_acoustic_field import visualize

from data_storage.combine_files_post_storage import (
    stitch_together_pickle_history_lists_and_store,
)

# from plotting.arena_module import ArenaModule
# from plotting.info_text_module import InfoTextModule
# from plotting.polarization_milling_module import PolarizationMillingModule
# from plotting.sensory_volume_module import SensoryVolumeModule
from plotting.visualizer import visualize
from simulation.class_simulation import Simulation


@hydra.main(version_base=None, config_path="../core/config/", config_name="config")
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
    timestamp = "_".join(hydra_job_dir.split("/")[-2:])  # "2025-04-05_12-34-56"
    print(f"OUTPUT_DIR = {OUTPUT_DIR}\n\nConfig = {cfg}\n")

    steps = int(np.floor(1.0 / (cfg.arena.FRAME_RATE * cfg.arena.TIME_STEP)))
    print(f"Skipped between video frames = {steps}")

    sim = Simulation(cfg, OUTPUT_DIR, store_history=True, store_data_for_plotting=True)
    sim.run()

    visualize(
        output_dir=OUTPUT_DIR,
        save_animation=OUTPUT_DIR,
        unique_id=timestamp,
        steps=max(1, steps),
        show_sounds=False,
        focal_bat=0,
        rows=1,
        columns=3,
        modules=[
            "arena",
            "polarization_milling",
            "info_text",
            # "ipi_radial",
            # "sum_radial",
            # "sensory_volume",
        ],
    )


if __name__ == "__main__":
    run_simulation()

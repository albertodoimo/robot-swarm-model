import random
import sys
import uuid

import hydra
import numpy as np
from omegaconf import DictConfig

sys.path.extend(["./src/", "./scripts/"])

from plotting.sim_plotter_single_bat_acoustic_field import visualize

from simulation.class_simulation import Simulation


@hydra.main(version_base=None, config_path="../config/", config_name="config")
def run_simulation(cfg: DictConfig) -> None:
    random.seed(cfg.arena.seed)
    np.random.seed(cfg.arena.seed)
    hydra_dir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    OUTPUT_DIR = hydra_dir
    print(OUTPUT_DIR)
    print(cfg)
    sim = Simulation(cfg, OUTPUT_DIR)
    sim.run()
    # unique_id = uuid.uuid4()
    # visualize(
    #     output_dir=OUTPUT_DIR,
    #     save_animation=hydra_dir,
    #     unique_id=unique_id,
    #     resolution=50,
    #     show_sounds=False,
    #     focal_bat=0,
    # )


if __name__ == "__main__":
    run_simulation()

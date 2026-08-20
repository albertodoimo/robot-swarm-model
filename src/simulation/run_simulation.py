import random
import sys

import hydra
from omegaconf import DictConfig

sys.path.extend(["./src/", "./scripts/"])

from simulation.class_simulation import Simulation


@hydra.main(version_base=None, config_path="../config/", config_name="config")
def run_simulation(cfg: DictConfig) -> None:
    random.seed(cfg.arena.seed)

    OUTPUT_DIR = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    print(OUTPUT_DIR)
    print(cfg)
    sim = Simulation(cfg, OUTPUT_DIR)
    sim.run()


if __name__ == "__main__":
    run_simulation()

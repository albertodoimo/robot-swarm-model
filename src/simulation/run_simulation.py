import random
import sys
import uuid

import hydra
import numpy as np
from omegaconf import DictConfig

sys.path.extend(["./src/", "./scripts/"])

# from plotting.sim_plotter_single_bat_acoustic_field import visualize

from simulation.class_simulation import Simulation
from plotting.arena_module import ArenaModule
from plotting.info_text_module import InfoTextModule
from plotting.polarization_milling_module import PolarizationMillingModule
from plotting.sensory_volume_module import SensoryVolumeModule
from plotting.visualizer import visualize

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
    # OUTPUT_DIR = r"/home/adityamoger/Documents/GitHub/bat-swarm-model/outputs/2026-09-06/00-59-33/"
    visualize(
        output_dir=OUTPUT_DIR,
        save_animation=OUTPUT_DIR,
        unique_id="plots",
        resolution=30,
        show_sounds=False,
        focal_bat=0,
        modules=[
            ArenaModule,
            PolarizationMillingModule,
            "info_text",
            "ipi_radial",
            "sum_radial",
            "sensory_volume",
        ],
       
    )


if __name__ == "__main__":
    run_simulation()

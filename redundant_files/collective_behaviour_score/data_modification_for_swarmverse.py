"""parsing data for swarmverse"""

import glob
import pickle
import sys

import numpy as np
import pandas as pd

sys.path.append("./scripts/plotting/")
sys.path.append("./src/")
from sim_plotter_single_bat_acoustic_field import stitch_together_history_lists


def load_and_convert_files(folder_dir, resolution):
    # history_data = load_history_dump(folder_dir)
    # bat_position_data = filter_bat_positions_from_history(history_data)
    history = stitch_together_history_lists(folder_dir)[0]
    bat_position_data = history[::resolution]
    swarmverse_compliant_file = {"id": [], "x": [], "y": [], "frame": [], "time": []}
    for frame, position_data in enumerate(bat_position_data):
        for i, bat_frame_position in enumerate(position_data["bat_positions"]):
            swarmverse_compliant_file["id"].append(i)
            swarmverse_compliant_file["x"].append(bat_frame_position[0])
            swarmverse_compliant_file["y"].append(bat_frame_position[1])
            swarmverse_compliant_file["frame"].append(frame)
            swarmverse_compliant_file["time"].append(position_data["time"])

    output_file = pd.DataFrame.from_dict(swarmverse_compliant_file)
    return output_file


if __name__ == "__main__":
    OUTPUT_DIR = (
        r"/home/adityamoger/Documents/GitHub/bat-swarm-model/outputs/18-09-05/12"
    )
    df = load_and_convert_files(OUTPUT_DIR, 1)
    df.to_csv(OUTPUT_DIR + "/0.csv")

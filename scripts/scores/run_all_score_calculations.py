import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.append("./scripts/")

from scores.calling_effort_score import calling_effort
from scores.collision_scores_single_bat import (
    compute_collision_counts_and_length,
    compute_collision_rate,
)
from scores.milling_score import compute_milling
from scores.nearest_neighbour_distance import compute_nearest_neighbour_distance
from scores.polarization_score import compute_polarization
from scores.space_occupied_scores import space_occupied_score


def load_history_dump(folder_path):
    """Load and merge all history dump files in a folder by time order"""

    pattern = os.path.join(folder_path, "history_dump_*.npz")
    npz_files = glob.glob(pattern)

    if not npz_files:
        print(f"No history dump files found in {folder_path}")
        return []

    # extract timestamps from filenames and sort by time
    file_times = []
    for file_path in npz_files:
        try:

            filename = os.path.basename(file_path)
            time_str = filename.replace("history_dump_", "").replace(".npz", "")
            timestamp = float(time_str)
            file_times.append((timestamp, file_path))
        except ValueError:
            print(f"could not parse timestamp from filename: {filename}")
            continue

    file_times.sort(key=lambda x: x[0])
    all_frames = []

    for timestamp, file_path in file_times:
        # print(f"Loading: {os.path.basename(file_path)} (time: {timestamp})")

        data = np.load(file_path)
        times = data["times"]
        positions_array = data["positions"]
        directions_array = data["directions"]
        # call_times_array = data["bat_call_time"]
        for i, frame_time in enumerate(times):
            frame_data = positions_array[i]
            frame_direction_data = directions_array[i]

            valid_positions = frame_data[~np.isnan(frame_data)]
            valid_directions = frame_direction_data[~np.isnan(frame_direction_data)]

            bat_positions = np.array(
                [
                    (valid_positions[j], valid_positions[j + 1])
                    for j in range(0, len(valid_positions), 2)
                ]
            )
            bat_directions = np.array(
                [
                    (valid_directions[j], valid_directions[j + 1])
                    for j in range(0, len(valid_directions), 2)
                ]
            )
            # bat_call_time = np.array([])

            all_frames.append(
                {
                    "time": np.round(frame_time, 3),
                    "bat_positions": bat_positions[:],
                    "bat_directions": bat_directions[:],
                    # "bat_positions_y": bat_positions[:, 1],
                    # "bat_call_time": bat_call_time
                }
            )
    all_frames.sort(key=lambda x: x["time"])
    return all_frames


def filter_bat_positions_from_history(all_frames):

    store_only_positions = []
    store_only_directions = []

    for item in all_frames:
        # print(item)
        store_only_positions.append(item["bat_positions"])
        store_only_directions.append(item["bat_directions"])

    return store_only_positions, store_only_directions


def reformat_history(history, focal_bat, parameter_df, iteration_label):
    # get time, position, call time data
    # reformat into long csv
    subset_of_focal_bat = []
    for item in history:
        reformatted_item = {
            "time": item["time"],
            "bat_position_x": item["bat_positions"][focal_bat][0],
            "bat_position_y": item["bat_positions"][focal_bat][1],
            "bat_call_time": item["bat_call_time"][focal_bat],
            "iteration_number": iteration_label,
        }
        reformatted_item.update(parameter_df.copy())
        subset_of_focal_bat.append(reformatted_item)

    # df_position_data = pd.DataFrame.from_dict(subset_of_focal_bat, orient="columns")
    # print(df_position_data)
    return subset_of_focal_bat


def take_history_store_scores(sim, sim_iteration_number):
    focal_bat = sim.bats[0]
    bat_positions = filter_bat_positions_from_history(sim.history)

    space_occupied = space_occupied_score(sim.parameters_df, bat_positions)
    collision_counts = compute_collision_counts_and_length(
        bat_positions, sim.parameters_df
    )
    collision_rate = compute_collision_rate(bat_positions, sim.parameters_df)
    calling_effort_score = calling_effort(focal_bat)

    dict_to_store = {
        "space_occupied": space_occupied,
        "collision_counts": collision_counts,
        "collision_rate": collision_rate,
        "calling_effort": calling_effort_score,
        "iteration_label": sim_iteration_number,
    }
    dict_to_store.update(sim.parameters_df)

    return dict_to_store


if __name__ == "__main__":
    output_dir = r"/home/adityamoger/Documents/GitHub/bat-swarm-model/multirun/2026-09-02/17-52-52/15/data/"
    bat_positions_raw = load_history_dump(output_dir)
    bat_positions, bat_directions = filter_bat_positions_from_history(bat_positions_raw)
    x = np.array(bat_directions, dtype=np.half)
    print(x.shape)

    import matplotlib.pyplot as plt

    def running_mean(x, N):
        cumsum = np.cumsum(np.insert(x, 0, 0))
        return (cumsum[N:] - cumsum[:-N]) / float(N)

    milling_score_timeseries = compute_milling(
        bat_directions=bat_directions, bat_positions=bat_positions
    )
    polarization_score_timeseries = compute_polarization(bat_directions)
    nnd_timeseries = compute_nearest_neighbour_distance(bat_positions)
    median_nnd_time_series = np.median(nnd_timeseries, axis=1)

    milling_score_timeseries = running_mean(milling_score_timeseries, 1000)
    polarization_score_timeseries = running_mean(polarization_score_timeseries, 1000)
    median_nnd_time_series = running_mean(median_nnd_time_series, 1000)
    plt.subplot(1, 2, 1)
    plt.plot(milling_score_timeseries, label="milling")
    plt.plot(polarization_score_timeseries, label="polarization")
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(median_nnd_time_series, label="nnd")
    plt.legend()
    plt.show()

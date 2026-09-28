import json
import pickle

import numpy as np

# import


def handle_data_storage_for_plotting(
    current_time,
    is_end_of_code,
    history,
    parameters_df,
    dir_to_store,
    store_data_for_plotting=True,
):
    """Generates files for data used for plotting.
    Periodically the history list is cleared to ensure
    RAM doesnt get used up.
    """
    if not store_data_for_plotting:
        return None
    else:
        history_array_size_limit = parameters_df["CLEANUP_PLOT_DATA"]

        if len(history) >= history_array_size_limit or is_end_of_code:
            time_stamp = f"{current_time:.4f}".zfill(9)
            with open(dir_to_store + f"history_dump_{time_stamp}.pkl", "wb") as f:
                pickle.dump(history, f)

        if is_end_of_code:
            with open(
                dir_to_store + "/parameters_used.json", "w", encoding="utf-8"
            ) as fp:
                json.dump(parameters_df, fp)


def handle_data_storage_for_scoring(
    current_time,
    is_end_of_code,
    history,
    parameters_df,
    dir_to_store,
    store_data_for_plotting=True,
):
    """Generates files for data used for plotting.
    Periodically the history list is cleared to ensure
    RAM doesnt get used up.
    """
    history_array_size_limit = parameters_df["CLEANUP_PLOT_DATA"]

    if len(history) >= history_array_size_limit or is_end_of_code:
        # Save current batch as compressed numpy file instead of pickle
        filename = dir_to_store + f"history_dump_{current_time:.3f}.npz"

        # Convert history to compact numpy format
        times = []
        positions = []
        directions = []
        for frame in history:
            times.append(frame["time"])
            frame_positions = []
            frame_directions = []
            for bat_pos in frame["bat_positions"]:
                frame_positions.extend([bat_pos[0], bat_pos[1]])
            for bat_dir in frame["bat_directions"]:
                frame_directions.extend([bat_dir[0], bat_dir[1]])
            positions.append(frame_positions)
            directions.append(frame_directions)

        # Save as compressed numpy
        times_array = np.array(times, dtype="f4")
        max_bats = max(len(frame) // 2 for frame in positions) if positions else 0
        positions_array = np.full((len(positions), max_bats * 2), np.nan, dtype="f4")
        directions_array = np.full((len(directions), max_bats * 2), np.nan, dtype="f4")

        for i, frame in enumerate(positions):
            positions_array[i, : len(frame)] = frame
        for i, frame in enumerate(directions):
            directions_array[i, : len(frame)] = frame

        np.savez_compressed(
            filename,
            times=times_array,
            positions=positions_array,
            directions=directions_array,
        )

    if is_end_of_code:
        with open(dir_to_store + "/parameters_used.json", "w", encoding="utf-8") as fp:
            json.dump(parameters_df, fp)


def handle_data_storage(
    current_time,
    is_end_of_code,
    history,
    parameters_df,
    dir_to_store,
    store_data_for_plotting=True,
):

    handle_data_storage_for_scoring(
        current_time,
        is_end_of_code,
        history,
        parameters_df,
        dir_to_store,
        store_data_for_plotting,
    )
    handle_data_storage_for_plotting(
        current_time,
        is_end_of_code,
        history,
        parameters_df,
        dir_to_store,
        store_data_for_plotting,
    )

    history_array_size_limit = parameters_df["CLEANUP_PLOT_DATA"]
    if len(history) >= history_array_size_limit or is_end_of_code:

        return True
    else:
        return False

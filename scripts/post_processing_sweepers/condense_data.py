import glob
import pickle

import numpy as np


def stitch_together_history_lists(history_output_dir):
    """Merges lists from all the pickle files together.

    Args:
        history_output_dir (string):

    Returns:
        list: list with all the merged lists from pickle files.
    """
    history_output_dir = history_output_dir  # + "/data_for_plotting/"
    list_of_dict_files = glob.glob(history_output_dir + "/history_dump_*.pkl")
    list_of_dict_files = np.sort(list_of_dict_files)

    list_containing_data_from_all_pickle_files = []
    for pickle_file in list_of_dict_files:
        with open(pickle_file, "rb") as f:
            _list_containing_subset = pickle.load(f)
            list_containing_data_from_all_pickle_files.extend(_list_containing_subset)

    parameter_file = glob.glob(history_output_dir + "/parameters_used.json")[0]
    parameter_df = load_parameters(parameter_file)

    with open(history_output_dir + "/bats_initial.pkl", "rb") as f:
        bats_initial_positions = pickle.load(f)
    with open(history_output_dir + "/obstacles_initial.pkl", "rb") as f:
        obstacles_initial_positions = pickle.load(f)
    with open(history_output_dir + "/jammers_initial.pkl", "rb") as f:
        jammers_initial_positions = pickle.load(f)

    times = [i["time"] for i in list_containing_data_from_all_pickle_files]
    sorting_indices = np.argsort(times)
    list_containing_data_from_all_pickle_files = np.array(
        list_containing_data_from_all_pickle_files
    )
    list_containing_data_from_all_pickle_files = (
        list_containing_data_from_all_pickle_files[sorting_indices]
    )

    return (
        list_containing_data_from_all_pickle_files,
        parameter_df,
        bats_initial_positions,
        obstacles_initial_positions,
        jammers_initial_positions,
    )

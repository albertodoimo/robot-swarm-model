import glob
import pickle

import numpy as np
from supporting_files.utilities import load_parameters, make_dir
from tqdm.rich import tqdm


def stitch_together_pickle_history_lists_and_store(
    history_output_dir, dir_to_store, id_for_simulation
):
    """Merges lists from all the pickle files together.

    Args:
        history_output_dir (string):

    Returns:
        list: list with all the merged lists from pickle files.
    """

    list_of_dict_files = glob.glob(history_output_dir + "/history_dump_*.pkl")
    list_of_dict_files = np.sort(list_of_dict_files)

    list_containing_data_from_all_pickle_files = []
    for pickle_file in tqdm(list_of_dict_files, desc="reading dict files "):
        with open(pickle_file, "rb") as f:
            _list_containing_subset = pickle.load(f)
            list_containing_data_from_all_pickle_files.extend(_list_containing_subset)
    print(id_for_simulation)
    parameter_file = glob.glob(history_output_dir + "/parameters_used.json")[0]
    parameter_df = load_parameters(parameter_file)
    print(parameter_df)
    times = [i["time"] for i in list_containing_data_from_all_pickle_files]
    sorting_indices = np.argsort(times)
    list_containing_data_from_all_pickle_files = np.array(
        list_containing_data_from_all_pickle_files
    )
    list_containing_data_from_all_pickle_files = (
        list_containing_data_from_all_pickle_files[sorting_indices]
    )
    # list_containing_data_from_all_pickle_files.append(parameter_df)
    np.append(list_containing_data_from_all_pickle_files, parameter_df)
    make_dir(dir_to_store)
    with open(dir_to_store + f"/history_dump_{id_for_simulation}.pkl", "wb") as f:
        pickle.dump(list_containing_data_from_all_pickle_files, f)
    return list_containing_data_from_all_pickle_files

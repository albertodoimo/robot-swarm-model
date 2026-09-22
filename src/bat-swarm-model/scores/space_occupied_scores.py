import bisect

import numpy as np


def space_occupied_score(parameters_df, bat_positions):
    """Score that handles space occupied by the agent in an arena
    Partition the space into coarse grid cells (0.5 m x 0.5 m) and count
    how many the agent walked over.
    Args:
        parameters_df (dict): parameter file of the simulation
        bat_positions (list of Vectors): position of bat at every timestep

    Returns:
        int: number of unique grid cells agent was in
    """
    # TODO : make this multi bat compatible.
    arena_width = parameters_df["ARENA_WIDTH"]
    arena_length = parameters_df["ARENA_LENGTH"]

    x = np.arange(0, arena_width, 0.5)
    y = np.arange(0, arena_length, 0.5)

    track_unique_cells = []
    # print(bat_positions)
    for bat_position_frame in bat_positions:
        # print(bat_position_frame)
        grid_x_index = bisect.bisect_left(x, bat_position_frame[0][0])
        grid_y_index = bisect.bisect_left(y, bat_position_frame[0][1])
        grid_cell_identity = str([grid_x_index, grid_y_index])

        if grid_cell_identity not in track_unique_cells:
            track_unique_cells.append(grid_cell_identity)
    total_cells = len(x) * len(y)

    return len(track_unique_cells)

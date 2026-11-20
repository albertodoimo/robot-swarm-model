import numpy as np
from movement_decision.supporting_functions_for_consistency import (  # given_matrix_find_cell_to_respond_to_absence,
    convert_detected_sounds_into_grids,
    given_matrix_find_cell_to_respond_to_presence,
    given_time_and_angle_return_direction,
)
from movement_decision.supporting_functions_for_loudest_sound import (
    convert_detected_sounds_into_grids_loudest_sound,
    given_angle_return_direction_to_sound,
    given_matrix_find_cell_to_respond_to_loudest_sound,
    given_time_and_angle_return_direction_loudest_sound,
    select_cell_to_respond_to,
)
from supporting_files.vectors import Vector


def decide_next_direction_based_on_consistency(self, detected_sound_objects):
    """decide next direction of bat based on sound

    Args:
        detected_sound_objects (list): list containing detected sounds
    """
    len_cap_memory_window = self.parameters_df["MEMORY_WINDOW_FOR_CONSISTENCY"]
    number_of_consistent_ipis_for_behaviour = int(
        np.ceil(self.parameters_df["MEMORY_WINDOW_FOR_CONSISTENCY"] / 2)
    )
    grid_for_current_ipi, grid_row_labels, grid_column_labels = (
        convert_detected_sounds_into_grids(
            detected_sound_objects,
            self.parameters_df,
            self.direction,
            self.allocentric_axis_y,
        )
    )
    self.memory_window_to_store_grids.append(grid_for_current_ipi)

    length_of_memory_window = len(self.memory_window_to_store_grids)
    if length_of_memory_window > len_cap_memory_window:
        self.memory_window_to_store_grids.pop(0)
    elif length_of_memory_window <= len_cap_memory_window:
        number_of_consistent_ipis_for_behaviour = np.min(
            [number_of_consistent_ipis_for_behaviour, length_of_memory_window - 1]
        )

    grids_to_consider_for_direction_change = self.memory_window_to_store_grids.copy()
    sum_grids_in_memory = np.sum(grids_to_consider_for_direction_change, axis=0)

    self.memory_window_sum_matrix = sum_grids_in_memory.copy()
    self.ipi_matrix_for_consistency = grids_to_consider_for_direction_change[-1]

    cell_index_to_respond_to = given_matrix_find_cell_to_respond_to_presence(
        sum_grids_in_memory,
        number_of_consistent_ipis_for_behaviour,
        self.parameters_df,
        self.direction,
        self.allocentric_axis_y,
        self.cell_index_to_respond_to,
    )

    self.cell_index_to_respond_to = cell_index_to_respond_to
    if np.isnan(cell_index_to_respond_to[0]):
        next_direction = self.next_direction
        response_type = None
        self.any_consistent_sound = "no"
        time_delay_of_activated_cell = np.nan

    else:
        time_delay_of_activated_cell = grid_row_labels[cell_index_to_respond_to[0]]
        angle_of_activated_cell = grid_column_labels[cell_index_to_respond_to[1]]
        next_direction, response_type = given_time_and_angle_return_direction(
            angle_of_activated_cell,
            self.parameters_df,
            self.direction,
            self.allocentric_axis_y,
        )
        self.any_consistent_sound = "yes"

    # # TODO : min delay implementation for slowing down
    # min_delay = np.inf
    # for sound_object in detected_sound_objects:
    #     delta_t = (
    #         np.array(sound_object["occurance_times"])[0]
    #         - sound_object["bat_last_call_time"]
    #     )
    #     min_delay = min(min_delay, delta_t)
    #     print(min_delay, delta_t)
    # if min_delay == np.inf:
    #     min_delay = np.nan
    self.first_detection_time_delay = time_delay_of_activated_cell

    return next_direction.normalize(), response_type


def decide_next_direction_based_on_loudness(self, detected_sound_objects):
    """decide next direction of bat based on sound

    Args:
        detected_sound_objects (list): list containing detected sounds
    """

    self.ipi_matrix_for_sensory_volume, grid_column_labels = (
        convert_detected_sounds_into_grids_loudest_sound(
            detected_sound_objects,
            self.parameters_df,
            self.direction,
            self.allocentric_axis_y,
        )
    )

    cell_index_to_respond_to = given_matrix_find_cell_to_respond_to_loudest_sound(
        self.ipi_matrix_for_sensory_volume,
        self.parameters_df,
        self.direction,
        self.allocentric_axis_y,
        self.id,
        self.cell_index_to_respond_to,
    )

    self.cell_index_to_respond_to = cell_index_to_respond_to

    if np.isnan(cell_index_to_respond_to[0]):
        # nothing to respond to: keep the current heading. Same as before when the
        # target is reset at each call; with TURN_THROUGH_CALLS it stops an old turn.
        next_direction = self.direction
        response_type = None
        self.any_loud_sound = "no"

    else:
        intensity_of_sound = self.ipi_matrix_for_sensory_volume[
            cell_index_to_respond_to
        ]
        angle_of_activated_cell = grid_column_labels[cell_index_to_respond_to[1]]
        next_direction, response_type = (
            given_time_and_angle_return_direction_loudest_sound(
                intensity_of_sound,
                angle_of_activated_cell,
                self.parameters_df,
                self.direction,
                self.allocentric_axis_y,
            )
        )
        self.any_loud_sound = "yes"
        # print(next_direction.normalize(), angle_of_activated_cell, intensity_of_sound)

    self.ipi_matrix_for_sensory_volume = self.ipi_matrix_for_sensory_volume[0]
    return next_direction.normalize(), response_type


def decide_next_direction_based_on_force(self, detected_sound_objects):
    """decide the response of the bat with the force based rule,
    the per-agent version of force_based_spherical (Ferrante et al. 2012).
    Called once per ipi, like decide_next_direction_based_on_loudness.

    Distances are replaced by received spl: the zone of attraction is every sound
    louder than SPL_THRESHOLD_FOR_ATTRACTION, the zone of repulsion every sound
    louder than SPL_THRESHOLD_FOR_REPULSION. One cell above the attraction
    threshold is picked (NEIGHBOUR_SELECTION) and its force is

        f = k * ln(10) / 20 * (SPL_THRESHOLD_FOR_REPULSION - spl)

    which is k * ln(r / zor) of the distance model, since spherical spreading drops
    20 * log10(r) dB. f > 0 attracts, f < 0 repels. The turn per time step and the
    speed are computed here once, from the angle to the sound at the decision.

    Args:
        detected_sound_objects (list): list containing detected sounds

    Returns:
        tuple: direction to the selected sound (Vector), response type,
            turn per time step (radians), speed (m/s)
    """
    time_step = self.parameters_df["TIME_STEP"]
    cruise_speed = self.parameters_df["BAT_FAST_SPEED"]

    sensory_grid, grid_column_labels = (
        convert_detected_sounds_into_grids_loudest_sound(
            detected_sound_objects,
            self.parameters_df,
            self.direction,
            self.allocentric_axis_y,
        )
    )
    self.ipi_matrix_for_sensory_volume = sensory_grid[0]

    spl_threshold_for_attraction = self.parameters_df["SPL_THRESHOLD_FOR_ATTRACTION"]
    if not np.any(sensory_grid > spl_threshold_for_attraction):
        # nobody in the zone of attraction: keep the heading at cruise speed
        self.cell_index_to_respond_to = (np.nan, np.nan)
        self.any_loud_sound = "no"
        self.response_force = 0.0
        return self.direction, None, 0.0, cruise_speed

    selected_cell = select_cell_to_respond_to(
        sensory_grid,
        spl_threshold_for_attraction,
        self.parameters_df.get("NEIGHBOUR_SELECTION", "loudest"),
    )
    self.cell_index_to_respond_to = (0, selected_cell)
    self.any_loud_sound = "yes"

    spl_of_selected_cell = sensory_grid[0, selected_cell]
    force = (
        self.parameters_df["FORCE_STIFFNESS"]
        * np.log(10)
        / 20
        * (self.parameters_df["SPL_THRESHOLD_FOR_REPULSION"] - spl_of_selected_cell)
    )
    self.response_force = force

    direction_to_sound = given_angle_return_direction_to_sound(
        grid_column_labels[selected_cell],
        self.parameters_df,
        self.direction,
        self.allocentric_axis_y,
    )
    # signed angle from heading to the sound, counter-clockwise positive
    angle_to_sound = self.direction.angle_between(direction_to_sound)

    max_turn_per_step = (
        np.radians(self.parameters_df["FORCE_MAX_ROTATION_SPEED"]) * time_step
    )
    turn_per_step = np.clip(
        self.parameters_df["FORCE_TURNING_GAIN"] * force * angle_to_sound * time_step,
        -max_turn_per_step,
        max_turn_per_step,
    )
    # speed up / slow down along the heading, never backwards nor above the cap
    speed = np.clip(
        self.parameters_df["FORCE_SPEED_GAIN"] * force * np.cos(angle_to_sound)
        + cruise_speed,
        0.0,
        self.parameters_df["FORCE_MAX_SPEED"],
    )
    response_type = "attraction_passive" if force > 0 else "repulsion_passive"

    return direction_to_sound, response_type, turn_per_step, speed

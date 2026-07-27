import bisect
import sys

import numpy as np

sys.path.append("./src/")
from supporting_files.utilities import str2bool


def find_sum_of_db(list_of_spls):
    """Computes the sum of all the spls in a given list.

    Args:
        list_of_spls (list): contains all the spls (in dB scale) that need to be added

    Returns:
        float: sum of spls in the list (in dB scale)
    """
    _temporary_sum = 0
    for spl in list_of_spls:
        if spl != 0:
            _temporary_sum += 10 ** (spl / 20)
    if _temporary_sum == 0:
        return 0
    sum_of_spls_in_db = 20 * np.log10(_temporary_sum)
    return np.round(sum_of_spls_in_db, 2)


def generate_empty_matrix(parameters_df):
    """generate an empty matrix to store sensory volume information

    Args:
        parameters_df (dict): parameter file used for the simulations

    Returns:
        tuple : first matrix is the empty matrix and
        second is the reference list of angles for columns.
    """
    # radial_resolution = parameters_df["BAT_RADIAL_RESOLUTION"]
    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"])
    # post_call_sampling_interval = parameters_df["RESPONSE_DELAY_LOUDEST_SOUND"]

    # spatial_grid_r = np.arange(
    #     call_duration,
    #     post_call_sampling_interval + radial_resolution,
    #     radial_resolution,
    # )
    spatial_grid_theta = np.arange(-np.pi, np.pi, angular_resolution)
    matrix_spatial_grid = np.zeros(shape=(1, len(spatial_grid_theta)))
    return matrix_spatial_grid, spatial_grid_theta


def convert_detected_sounds_into_grids_loudest_sound(
    heard_sounds, parameters_df, bat_direction, allocentric_axis_y
):
    spatial_reference_frame = parameters_df["SPATIAL_REFERENCE_FRAME"]
    # convert_grid_to_one_hot = str2bool(parameters_df["CONVERT_GRIDS+TO_ONE_HOT_?"])

    matrix_spatial_grid, spatial_grid_theta = generate_empty_matrix(parameters_df)
    store_grid = matrix_spatial_grid.copy()
    store_grid_sum = matrix_spatial_grid.copy()

    if len(heard_sounds) == 0:
        return store_grid_sum, spatial_grid_theta

    for sound_object in heard_sounds:

        if spatial_reference_frame == "allocentric":
            theta = allocentric_axis_y.angle_between(sound_object["incident_direction"])
        elif spatial_reference_frame == "egocentric":
            theta = bat_direction.angle_between(sound_object["incident_direction"])
        else:
            raise ValueError("not a supported spatial reference frame")

        grid_column_index = bisect.bisect_left(spatial_grid_theta, theta)

        # angles are circular
        if grid_column_index == len(spatial_grid_theta):
            grid_column_index = 0

        sound_max_intensity = np.max(sound_object["all_spl_values"])

        # if store_grid[0, grid_column_index] >= sound_max_intensity:
        #     continue
        if store_grid[0, grid_column_index] < sound_max_intensity:
            store_grid[0, grid_column_index] = sound_max_intensity

        store_grid_sum[0, grid_column_index] = find_sum_of_db(
            [store_grid_sum[0, grid_column_index], sound_max_intensity]
        )
        # print(f"max db in cells : {store_grid}")
        # print(f"sum of db in cells : {store_grid_sum}")

    return store_grid, spatial_grid_theta


def given_matrix_find_cell_to_respond_to_loudest_sound(matrix, parameters_df):
    matrix = np.matrix(matrix)
    print(matrix)
    loudest_cell = np.argmax(matrix)
    output_cell_number = (0, loudest_cell)
    intensity_threshold_for_attraction = parameters_df["SPL_THRESHOLD_FOR_ATTRACTION"]
    print(matrix[output_cell_number])
    if matrix[output_cell_number] < intensity_threshold_for_attraction:
        output_cell_number = [np.nan, np.nan]
    return output_cell_number


def given_time_and_angle_return_direction_loudest_sound(
    intensity,
    angle_of_activated_cell,
    parameters_df,
    bat_direction,
    allocentric_axis_y,
):
    spatial_reference_frame = parameters_df["SPATIAL_REFERENCE_FRAME"]

    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"])

    noise_in_angle = np.random.uniform(-angular_resolution / 2, angular_resolution / 2)
    angle_of_next_direction = (
        angle_of_activated_cell - angular_resolution / 2 + noise_in_angle
    )
    intensity_threshold_for_repulsion = parameters_df["SPL_THRESHOLD_FOR_REPULSION"]
    intensity_threshold_for_attraction = parameters_df["SPL_THRESHOLD_FOR_ATTRACTION"]

    if spatial_reference_frame == "allocentric":
        angle_between_self_and_allocentric_axis = bat_direction.angle_between(
            allocentric_axis_y
        )
        angle_of_next_direction += angle_between_self_and_allocentric_axis

    if intensity >= intensity_threshold_for_repulsion:
        angle_of_next_direction += np.pi
        response_type = "repulsion"
    else:  # intensity >= intensity_threshold_for_attraction
        # print(f"attraction delay{corrected_time_delay}")
        response_type = "attraction"

    next_direction = bat_direction.rotate(angle_of_next_direction)

    return next_direction.normalize(), response_type


if __name__ == "__main__":
    dict_params = {
        "BAT_ANGULAR_RESOLUTION": 30,
        "CALL_DURATION": 2,
    }
    X, Y = generate_empty_matrix(parameters_df=dict_params)
    Z = np.matrix([[0, 1, 2, 1]])
    print(np.argmin(X))
    print(np.argmax(Z), Z[0, np.argmax(Z)])

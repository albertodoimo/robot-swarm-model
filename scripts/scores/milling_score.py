import numpy as np


def compute_milling(bat_directions, bat_positions):

    store_milling = []
    for i, direction_frame in enumerate(bat_directions):
        position_frame = bat_positions[i]
        normalized_vectors = [i / np.linalg.norm(i) for i in direction_frame]

        group_centriod = np.mean(position_frame, axis=0)

        difference_vector_from_mean = [i - group_centriod for i in position_frame]
        normalized_difference_from_mean = [
            i / np.linalg.norm(i) for i in difference_vector_from_mean
        ]

        cross_product_with_direction = [
            np.cross(normalized_difference_from_mean[i], normalized_vectors[i])
            for i in range(len(normalized_difference_from_mean))
        ]

        mean_cross_vector = np.mean(cross_product_with_direction, axis=0)
        # summed_vector = np.mean(normalized_vectors, axis=0)
        magnitude_of_mean_cross_vector = np.linalg.norm(mean_cross_vector)

        store_milling.append(magnitude_of_mean_cross_vector)
    median_milling = np.median(store_milling)
    return store_milling

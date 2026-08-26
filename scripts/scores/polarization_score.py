# implementation from jitesh jawar + guttal et al 2019 noise induced schooling in fishes.
# breif exaplination
# take the unit direction vectors of all the agents and sum them up.
# score is the length of the resultant vector
import numpy as np


def compute_polarization(bat_directions):

    store_polarization = []
    for direction_frame in bat_directions:
        # print(position_frame)
        normalized_vectors = [i / np.linalg.norm(i) for i in direction_frame]
        summed_vector = np.mean(normalized_vectors, axis=0)
        magnitude_of_summed_vector = np.linalg.norm(summed_vector)

        store_polarization.append(magnitude_of_summed_vector)
    median_polarization = np.median(store_polarization)
    return store_polarization


if __name__ == "__main__":
    x = [(0, 1), (1, 0)]
    y = np.mean(x, axis=0)
    z = np.dot(y, y)
    print(y, z)

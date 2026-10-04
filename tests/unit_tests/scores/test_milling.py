import sys
import unittest

import numpy as np

sys.path.extend(
    [
        "./src/bat-swarm-model/",
        "./src/bat-swarm-model/core/",
        "./src/bat-swarm-model/plot/",
    ]
)
from scores.milling_score import compute_milling  # Replace with actual import path


class TestComputeMilling(unittest.TestCase):
    def test_empty_input(self):
        self.assertTrue(np.isnan(compute_milling([], [])))

    def test_aligned_radially(self):
        # Bats arranged radially, all pointing toward center → high milling
        positions = [
            np.array([1, 0]),
            np.array([0, 1]),
            np.array([-1, 0]),
            np.array([0, -1]),
        ]
        rotation_matrix_90 = np.matrix([[0, 1], [-1, 0]])
        directions = [
            np.array(rotation_matrix_90 @ p).flatten() for p in positions
        ]  # All pointing toward center
        print(directions)
        score = compute_milling(directions, positions)
        self.assertGreater(score, 0.9)  # Should be high

    def test_random_motion(self):
        # Random directions → low milling
        positions = [np.array([i, i]) for i in range(3)]
        directions = [np.array([1, 0]), np.array([0, 1]), np.array([-1, 1])]
        score = compute_milling(directions, positions)
        self.assertLess(score, 0.5)  # Should be low


if __name__ == "__main__":
    unittest.main()

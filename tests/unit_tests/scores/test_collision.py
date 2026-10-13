"""
Tests for compute_collision_counts_and_length function
Using unittest (no pytest)
"""

import sys
import unittest

import numpy as np
import scipy as scp

sys.path.extend(
    [
        "./src/bat-swarm-model/",
        "./src/bat-swarm-model/core/",
        "./src/bat-swarm-model/plot/",
    ]
)
from scores.collision_scores import (
    compute_collision_counts_and_length,  # Replace with actual import path
)


class TestComputeCollisionCountsAndLength(unittest.TestCase):
    """Tests for compute_collision_counts_and_length function"""

    def test_no_collisions(self):
        """Test with no collisions"""
        params = {
            "ARENA_WIDTH": 10.0,
            "ARENA_LENGTH": 10.0,
            "BAT_RADIUS": 0.5,
        }
        # 2 bats, 2 time steps, positions far apart
        positions = [
            [[1.0, 1.0], [9.0, 9.0]],  # time step 1
            [[2.0, 2.0], [8.0, 8.0]],  # time step 2
        ]

        wall_collisions, bat_collisions, wall_ts, bat_ts = (
            compute_collision_counts_and_length(positions, params)
        )

        self.assertEqual(wall_collisions, 0)
        self.assertEqual(bat_collisions, 0)
        self.assertEqual(wall_ts, [0, 0])
        self.assertEqual(bat_ts, [0, 0])

    def test_wall_collisions(self):
        """Test with wall collisions"""
        params = {
            "ARENA_WIDTH": 10.0,
            "ARENA_LENGTH": 10.0,
            "BAT_RADIUS": 0.5,
        }
        # Bat at wall boundary
        positions = [
            [[0.5, 5.0]],  # time step 1 - bat at left wall
        ]

        wall_collisions, bat_collisions, wall_ts, bat_ts = (
            compute_collision_counts_and_length(positions, params)
        )

        self.assertEqual(wall_collisions, 1)
        self.assertEqual(bat_collisions, 0)
        self.assertEqual(wall_ts, [1])
        self.assertEqual(bat_ts, [0])

    def test_bat_bat_collisions(self):
        """Test with bat-bat collisions"""
        params = {
            "ARENA_WIDTH": 10.0,
            "ARENA_LENGTH": 10.0,
            "BAT_RADIUS": 0.5,
        }
        # 2 bats very close (collision)
        positions = [
            [[5.0, 5.0], [5.1, 5.0]],  # distance < 1.0 (2 * radius)
        ]

        wall_collisions, bat_collisions, wall_ts, bat_ts = (
            compute_collision_counts_and_length(positions, params)
        )

        self.assertEqual(wall_collisions, 0)
        self.assertEqual(bat_collisions, 1)
        self.assertEqual(wall_ts, [0])
        self.assertEqual(bat_ts, [1])


if __name__ == "__main__":
    unittest.main(verbosity=2)

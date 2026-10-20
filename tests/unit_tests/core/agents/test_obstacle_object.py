"""
Tests for the Obstacle class in src/bat_swarm_model/core/agents/class_obstacles.py
"""

import random
import sys
import unittest
from unittest.mock import patch

sys.path.extend(
    [
        "./src/robot-swarm-model/",
        "./src/robot-swarm-model/core/",
        "./src/robot-swarm-model/plot/",
    ]
)


from agents.class_obstacles import Obstacle
from supporting_files.vectors import Vector


class TestObstacleInitialization(unittest.TestCase):
    """tests for Obstacle initialization"""

    def setUp(self):

        self.mock_parameters_df = {
            "OBSTACLE_RADIUS": 1.0,
            "ARENA_WIDTH": 10.0,
            "ARENA_LENGTH": 10.0,
        }

    def test_initialization_with_random_position(self):
        """Test initialization with random position"""

        with patch("random.uniform") as mock_uniform:
            # return values for the two uniform calls (x and y coordinates)
            mock_uniform.side_effect = [3.0, 5.0]

            obstacle = Obstacle(self.mock_parameters_df, "random", 2.0)

            # position created with the mocked values check
            self.assertEqual(obstacle.position.x, 3.0)
            self.assertEqual(obstacle.position.y, 5.0)
            self.assertEqual(obstacle.radius, 2.0)

    def test_initialization_with_specific_position(self):
        """Test initialization with specific position"""
        position = (4.5, 7.2)
        obstacle = Obstacle(self.mock_parameters_df, position, 1.5)

        self.assertEqual(obstacle.position.x, 4.5)
        self.assertEqual(obstacle.position.y, 7.2)
        self.assertEqual(obstacle.radius, 1.5)

    def test_id_counter_increments(self):
        """Test that ID counter increments properly"""
        Obstacle._id_counter = 0
        obstacle1 = Obstacle(self.mock_parameters_df, "random", 1.0)
        obstacle2 = Obstacle(self.mock_parameters_df, "random", 1.0)
        obstacle3 = Obstacle(self.mock_parameters_df, "random", 1.0)

        self.assertEqual(obstacle1.id, 0)
        self.assertEqual(obstacle2.id, 1)
        self.assertEqual(obstacle3.id, 2)

    def test_id_counter_reset(self):
        """Test that ID counter can be reset"""
        obstacle1 = Obstacle(self.mock_parameters_df, "random", 1.0)
        obstacle2 = Obstacle(self.mock_parameters_df, "random", 1.0)

        # Reset the counter
        Obstacle._id_counter = 0

        obstacle3 = Obstacle(self.mock_parameters_df, "random", 1.0)

        self.assertEqual(obstacle3.id, 0)


class TestObstacleCheckCollision(unittest.TestCase):
    """Tests for the check_collision method"""

    def setUp(self):
        self.mock_parameters_df = {
            "OBSTACLE_RADIUS": 2.0,
            "ARENA_WIDTH": 10.0,
            "ARENA_LENGTH": 10.0,
        }

    def test_point_inside_obstacle(self):
        """Test collision detection for a point inside the obstacle"""
        # Create obstacle at origin with radius 2
        obstacle = Obstacle(self.mock_parameters_df, (0, 0), 2.0)

        # Point inside the obstacle (distance < radius)
        point = Vector(1.0, 0.0)  # distance = 1.0 < 2.0
        self.assertTrue(obstacle.check_collision(point))

    def test_point_on_obstacle_boundary(self):
        """Test collision detection for a point on the boundary"""
        # Create obstacle at origin with radius 2
        obstacle = Obstacle(self.mock_parameters_df, (0, 0), 2.0)

        # Point on the boundary (distance = radius)
        point = Vector(2.0, 0.0)  # distance = 2.0 = radius
        self.assertTrue(obstacle.check_collision(point))

    def test_point_outside_obstacle(self):
        """Test collision detection for a point outside the obstacle"""
        # Create obstacle at origin with radius 2
        obstacle = Obstacle(self.mock_parameters_df, (0, 0), 2.0)

        # Point outside the obstacle (distance > radius)
        point = Vector(3.0, 0.0)  # distance = 3.0 > 2.0
        self.assertFalse(obstacle.check_collision(point))

    def test_point_with_obstacle_not_at_origin(self):
        """Test collision detection for obstacle not at origin"""
        # Create obstacle at (3, 4) with radius 2
        obstacle = Obstacle(self.mock_parameters_df, (3, 4), 2.0)

        # Point inside the obstacle
        point = Vector(4.0, 4.0)  # distance = 1.0 < 2.0
        self.assertTrue(obstacle.check_collision(point))

        # Point outside the obstacle
        point = Vector(6.0, 4.0)  # distance = 3.0 > 2.0
        self.assertFalse(obstacle.check_collision(point))


class TestObstacleGetReflectionNormal(unittest.TestCase):
    """Tests for the get_reflection_normal method"""

    def setUp(self):
        self.mock_parameters_df = {
            "OBSTACLE_RADIUS": 2.0,
            "ARENA_WIDTH": 10.0,
            "ARENA_LENGTH": 10.0,
        }

    def test_normal_at_boundary_point(self):
        """Test normal vector at a boundary point"""
        # Create obstacle at origin
        obstacle = Obstacle(self.mock_parameters_df, (0, 0), 2.0)

        # Normal at (2, 0) should point in the x direction
        point = Vector(2.0, 0.0)
        normal = obstacle.get_reflection_normal(point)

        # The normal should be (1, 0) - pointing directly away from center
        self.assertAlmostEqual(normal.x, 1.0, places=3)
        self.assertAlmostEqual(normal.y, 0.0, places=3)

    def test_normal_at_different_boundary_point(self):
        """Test normal vector at a different boundary point"""
        # Create obstacle at origin
        obstacle = Obstacle(self.mock_parameters_df, (0, 0), 2.0)

        # Normal at (0, 2) should point in the y direction
        point = Vector(0.0, 2.0)
        normal = obstacle.get_reflection_normal(point)

        # The normal should be (0, 1) - pointing directly away from center
        self.assertAlmostEqual(normal.x, 0.0, places=3)
        self.assertAlmostEqual(normal.y, 1.0, places=3)

    def test_normal_with_obstacle_not_at_origin(self):
        """Test normal vector for obstacle not at origin"""
        # Create obstacle at (3, 4)
        obstacle = Obstacle(self.mock_parameters_df, (3, 4), 2.0)

        # Normal at (5, 4) - point on the right boundary
        point = Vector(5.0, 4.0)
        normal = obstacle.get_reflection_normal(point)

        # The normal should be (1, 0) - pointing directly away from center (3,4)
        self.assertAlmostEqual(normal.x, 1.0, places=3)
        self.assertAlmostEqual(normal.y, 0.0, places=3)


class TestObstacleEdgeCases(unittest.TestCase):
    """Tests for edge cases in the Obstacle class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_parameters_df = {
            "OBSTACLE_RADIUS": 1.0,
            "ARENA_WIDTH": 10.0,
            "ARENA_LENGTH": 10.0,
        }

    def test_zero_radius_obstacle(self):
        """Test obstacle with zero radius"""
        obstacle = Obstacle(self.mock_parameters_df, (5, 5), 0.0)

        # Point at the same position as obstacle center
        point = Vector(5.0, 5.0)
        self.assertTrue(obstacle.check_collision(point))  # distance = 0 <= 0

        # Point slightly away
        point = Vector(5.1, 5.0)
        self.assertFalse(obstacle.check_collision(point))  # distance = 0.1 > 0

    def test_very_large_obstacle(self):
        """Test obstacle with radius larger than arena"""
        # Create a very large obstacle
        large_parameters = self.mock_parameters_df.copy()
        large_parameters["OBSTACLE_RADIUS"] = 100.0

        obstacle = Obstacle(large_parameters, (5, 5), 100.0)

        # Any point should be inside this huge obstacle
        point = Vector(0, 0)
        self.assertTrue(obstacle.check_collision(point))

    def test_point_exactly_at_obstacle_center(self):
        """Test collision detection for point exactly at obstacle center"""
        obstacle = Obstacle(self.mock_parameters_df, (3, 4), 2.0)

        # Point at the center
        point = Vector(3.0, 4.0)
        self.assertTrue(obstacle.check_collision(point))  # distance = 0 <= 2.0

    def test_normal_at_obstacle_center_raises_error(self):
        """Test normal vector when point is at obstacle center"""
        obstacle = Obstacle(self.mock_parameters_df, (0, 0), 2.0)

        # Point at the center (this would cause division by zero in the normal calculation)
        point = Vector(0.0, 0.0)

        # This should raise a ZeroDivisionError
        with self.assertRaises(ZeroDivisionError):
            obstacle.get_reflection_normal(point)


if __name__ == "__main__":

    unittest.main(verbosity=2)

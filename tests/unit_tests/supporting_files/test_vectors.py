"""unit test to test sound propagation"""

import math
import sys
import unittest

import numpy as np

sys.path.append("./src/")
from supporting_files.vectors import Vector

# sys.path.insert(1, ".")


class TestVector(unittest.TestCase):
    def setUp(self):
        """Create common vectors for testing"""
        self.zero = Vector(0, 0)
        self.v1 = Vector(1, 0)
        self.v2 = Vector(0, 1)
        self.v3 = Vector(3, 4)  # 3-4-5 triangle
        self.v4 = Vector(-1, -1)
        self.v5 = Vector(1.123456, 2.654321)  # Test rounding

    def test_initialization(self):
        """Test vector creation and rounding"""
        self.assertEqual(self.v5.x, 1.12346)
        self.assertEqual(self.v5.y, 2.65432)
        self.assertEqual(Vector().x, 0.0)
        self.assertEqual(Vector().y, 0.0)

    def test_addition(self):
        """Test vector addition"""
        self.assertTrue((self.v1 + self.v2).compare(Vector(1, 1)))
        self.assertTrue((self.v3 + self.v4).compare(Vector(2, 3)))
        self.assertTrue((self.zero + self.v1).compare(self.v1))

    def test_subtraction(self):
        """Test vector subtraction"""
        self.assertTrue((self.v1 - self.v2).compare(Vector(1, -1)))
        self.assertTrue((self.v3 - self.v3).compare(self.zero))
        self.assertTrue((self.v4 - self.v1).compare(Vector(-2, -1)))

    def test_scalar_multiplication(self):
        """Test scalar multiplication"""
        self.assertTrue((self.v1 * 2).compare(Vector(2, 0)))
        self.assertTrue((self.v3 * 0.5).compare(Vector(1.5, 2)))
        self.assertTrue((self.v4 * -1).compare(Vector(1, 1)))
        self.assertTrue((self.zero * 100).compare(self.zero))

    def test_compare(self):
        """Test vector comparison"""
        self.assertTrue(self.v1.compare(Vector(1, 0)))
        self.assertTrue(self.zero.compare(Vector(0, 0)))
        self.assertFalse(self.v1.compare(self.v2))
        self.assertFalse(self.v1.compare(Vector(1.00001, 0)))

    def test_magnitude(self):
        """Test magnitude calculation"""
        self.assertAlmostEqual(self.zero.magnitude(), 0.0)
        self.assertAlmostEqual(self.v1.magnitude(), 1.0)
        self.assertAlmostEqual(self.v3.magnitude(), 5.0)  # 3-4-5 triangle
        self.assertAlmostEqual(self.v4.magnitude(), math.sqrt(2))

    def test_normalize(self):
        """Test vector normalization"""
        self.assertTrue(self.zero.normalize().compare(self.zero))
        self.assertTrue(self.v1.normalize().compare(self.v1))
        norm_v3 = self.v3.normalize()
        self.assertAlmostEqual(norm_v3.magnitude(), 1.0)
        self.assertAlmostEqual(norm_v3.x, 0.6)
        self.assertAlmostEqual(norm_v3.y, 0.8)

    def test_distance_to(self):
        """Test distance between vectors"""
        self.assertAlmostEqual(self.v1.distance_to(self.v2), math.sqrt(2))
        self.assertAlmostEqual(self.v3.distance_to(self.zero), 5.0)
        self.assertAlmostEqual(self.v1.distance_to(self.v1), 0.0)

    def test_angle_between(self):
        """Test angle between vectors"""
        # Test with same vector
        self.assertAlmostEqual(self.v1.angle_between(self.v1), 0.0)

        # Test with perpendicular vectors
        angle = self.v1.angle_between(self.v2)
        self.assertAlmostEqual(abs(angle), math.pi / 2)

        # Test with opposite vectors
        angle = self.v1.angle_between(Vector(-1, 0))
        self.assertAlmostEqual(abs(angle), math.pi)

        # Test with arbitrary vectors
        angle = self.v4.angle_between(self.v3)

        expected = math.atan2(4, 3) - math.atan2(-1, -1)
        expected = (expected + math.pi) % (math.pi * 2) - math.pi
        print(expected)
        self.assertAlmostEqual(angle, expected, places=4)

    def test_random_direction(self):
        """Test random direction generation"""
        for _ in range(10):  # Test multiple times
            v = self.v1.random_direction()
            self.assertAlmostEqual(v.magnitude(), 1.0, places=4)

    def test_reflect(self):
        """Test vector reflection"""
        # Reflect (1,0) about x-axis (normal = (0,1))
        reflected = self.v1.reflect(Vector(0, 1))
        self.assertTrue(reflected.compare(Vector(1, 0)))

        # Reflect (1,0) about y-axis (normal = (1,0))
        reflected = self.v1.reflect(Vector(1, 0))
        self.assertTrue(reflected.compare(Vector(-1, 0)))

        # Reflect (1,1) about (0,1)
        v = Vector(1, 1)
        normal = Vector(0, 1)
        reflected = v.reflect(normal)
        self.assertTrue(reflected.compare(Vector(1, -1)))

    def test_to_tuple(self):
        """Test conversion to tuple"""
        self.assertEqual(self.v1.to_tuple(), (1.0, 0.0))
        self.assertEqual(self.v3.to_tuple(), (3.0, 4.0))

    def test_rotate(self):
        """Test vector rotation"""
        # Rotate (1,0) by 90 degrees
        rotated = self.v1.rotate(math.pi / 2)
        self.assertTrue(rotated.compare(Vector(0, 1)))

        # Rotate (0,1) by 180 degrees
        rotated = self.v2.rotate(math.pi)
        self.assertTrue(rotated.compare(Vector(0, -1)))

        # Rotate (1,1) by 45 degrees
        v = Vector(1, 1)
        rotated = v.rotate(math.pi / 4)
        expected_x = math.cos(math.pi / 4) - math.sin(math.pi / 4)
        expected_y = math.sin(math.pi / 4) + math.cos(math.pi / 4)
        self.assertAlmostEqual(rotated.x, expected_x, places=5)
        self.assertAlmostEqual(rotated.y, expected_y, places=5)

    def test_rotation_matrix(self):
        """Test rotation matrix generation"""
        angle = math.pi / 2
        matrix = self.v1.rotation_matrix(angle)
        expected = np.matrix([[0, -1], [1, 0]])
        np.testing.assert_array_almost_equal(matrix, expected)

    def test_matrix_multiplication(self):
        """Test matrix multiplication"""
        angle = math.pi / 2
        matrix = self.v1.rotation_matrix(angle)
        result = self.v1.matrix_multiplication(matrix)
        self.assertTrue(result.compare(Vector(0, 1)))

    def test_repr(self):
        """Test string representation"""
        self.assertEqual(repr(self.v1), "Vector(1.000, 0.000)")
        self.assertEqual(repr(self.v3), "Vector(3.000, 4.000)")
        self.assertEqual(repr(Vector(1.23456, 2.34567)), "Vector(1.235, 2.346)")


if __name__ == "__main__":
    unittest.main()

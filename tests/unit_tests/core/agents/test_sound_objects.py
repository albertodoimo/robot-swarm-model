import math
import sys
import unittest
import uuid
from unittest.mock import MagicMock, patch

sys.path.extend(
    [
        "./src/bat-swarm-model/",
        "./src/bat-swarm-model/core/",
        "./src/bat-swarm-model/plot/",
    ]
)
from agents.class_sounds import (
    DirectSound,
    EchoSound,
)
from supporting_files.utilities import call_directionality_factor


class TestEchoSound(unittest.TestCase):
    def setUp(self):
        """Create common test fixtures"""
        # Mock parameters DataFrame
        self.parameters_df = {
            "SOUND_SPEED": 343.0,
            "ARENA_WIDTH": 100.0,
            "ARENA_LENGTH": 100.0,
            "CALL_DIRECTIONALITY": 0.5,
            "AIR_ABSORPTION": 0.01,
            "CALL_DURATION": 0.1,
            "HEARING_THRESHOLD": 20.0,
        }

        # Mock origin and direction vectors
        self.origin = MagicMock()
        self.origin.distance_to.return_value = 0.0
        self.direction_vector = MagicMock()
        self.direction_vector.angle_between.return_value = 0.0

        # Create test EchoSound
        self.echo_sound = EchoSound(
            parameters_df=self.parameters_df,
            origin=self.origin,
            creation_time=0.0,
            emitter_id="test_emitter",
            initial_spl=100.0,
            reflected_from="test_wall",
            direction_vector=self.direction_vector,
        )

    def test_initialization(self):
        """Test EchoSound initialization"""
        self.assertEqual(self.echo_sound.origin, self.origin)
        self.assertEqual(self.echo_sound.creation_time, 0.0)
        self.assertEqual(self.echo_sound.emitter_id, "test_emitter")
        self.assertEqual(self.echo_sound.initial_spl, 100.0)
        self.assertEqual(self.echo_sound.current_spl, 100.0)
        self.assertEqual(self.echo_sound.current_radius, 0.0)
        self.assertEqual(self.echo_sound.speed, 343.0)
        self.assertTrue(self.echo_sound.active)
        self.assertEqual(self.echo_sound.reflected_from, "test_wall")
        self.assertIsInstance(self.echo_sound.id, uuid.UUID)
        self.assertEqual(self.echo_sound.direction_vector, self.direction_vector)
        self.assertEqual(self.echo_sound.arena_width, 100.0)
        self.assertEqual(self.echo_sound.arena_length, 100.0)
        self.assertEqual(self.echo_sound.call_directionality, 0.5)

    def test_update(self):
        """Test sound propagation with time"""
        # Test at t=0
        self.echo_sound.update(0.0)
        self.assertEqual(self.echo_sound.current_radius, 0.0)
        self.assertEqual(self.echo_sound.current_spl, 100.0)

        # Test at t=1
        self.echo_sound.update(1.0)
        self.assertAlmostEqual(self.echo_sound.current_radius, 343.0)
        # SPL should decrease with distance and air absorption
        expected_spl = 100.0 - 20 * math.log10(343.0) - 0.01 * 343.0
        self.assertAlmostEqual(self.echo_sound.current_spl, expected_spl, places=2)

        # Test when sound goes outside arena
        self.echo_sound.update(300.0)  # Radius would be 343*300 > 100
        self.assertFalse(self.echo_sound.active)

    def test_contains_point(self):
        """Test if a point is within the sound disk"""
        # Mock point at distance 50
        point = MagicMock()
        self.origin.distance_to.return_value = 75.0
        # Current radius is 0, so should return False
        self.assertFalse(self.echo_sound.contains_point(point))

        # Update to make radius 100
        self.echo_sound.update(100 / 343.0)
        self.assertTrue(self.echo_sound.contains_point(point))

        # Test point at edge of sound disk
        self.origin.distance_to.return_value = 100.0
        self.assertTrue(self.echo_sound.contains_point(point))

        # Test point just outside
        self.origin.distance_to.return_value = 100.1
        self.assertFalse(self.echo_sound.contains_point(point))

        # Test with call duration effect
        self.origin.distance_to.return_value = 90.0  # 100 - 0.1*343 ≈ 96.57
        self.assertTrue(self.echo_sound.contains_point(point))

    def test_sound_directionality(self):
        """Test sound directionality calculation"""
        angle = math.pi / 4  # 45 degrees
        expected = call_directionality_factor(a=0.5, theta=angle)
        result = self.echo_sound.sound_directionality(angle)
        self.assertEqual(result, expected)

    def test_spl_at_receiver(self):
        """Test SPL calculation at receiver position"""
        # Mock receiver position
        receiver = MagicMock()
        receiver.distance_to.return_value = 10.0
        self.direction_vector.angle_between.return_value = math.pi / 4  # 45 degrees

        spl = self.echo_sound.spl_at_receiver(receiver)

        # Expected calculation:
        # distance_effect = 20 * log10(10) ≈ 20
        # air_absorption = 0.01 * 10 = 0.1
        # spl_corrected = 100 - 20 - 0.1 = 79.9
        # directionality = call_directionality_factor(0.5, pi/4)
        directionality = call_directionality_factor(a=0.5, theta=math.pi / 4)
        expected_spl = 100.0 - 20 * math.log10(10.0) - 0.01 * 10.0 + directionality
        self.assertAlmostEqual(spl, expected_spl, places=2)

        # Test when receiver is at origin
        receiver.distance_to.return_value = 0.0
        spl = self.echo_sound.spl_at_receiver(receiver)
        self.assertEqual(spl, 100.0 + directionality)  # initial_spl + directionality

    def test_check_if_sound_outside_arena(self):
        """Test arena boundary checking"""
        # Sound radius smaller than arena
        self.echo_sound.current_radius = 50.0
        self.assertFalse(self.echo_sound.check_if_sound_outside_arena())

        # Sound radius equal to arena
        self.echo_sound.current_radius = 100.0
        self.assertFalse(self.echo_sound.check_if_sound_outside_arena())

        # Sound radius larger than arena
        self.echo_sound.current_radius = 101.0
        self.assertTrue(self.echo_sound.check_if_sound_outside_arena())

    def test_repr(self):
        """Test string representation"""
        repr_str = repr(self.echo_sound)
        self.assertIn("EchoSound", repr_str)
        self.assertIn("origin=", repr_str)
        self.assertIn("radius=", repr_str)
        self.assertIn("spl=", repr_str)
        self.assertIn("emitter=", repr_str)
        self.assertIn("creation_time=", repr_str)


class TestDirectSound(unittest.TestCase):
    def setUp(self):
        """Create common test fixtures"""
        # Mock parameters DataFrame
        self.parameters_df = {
            "SOUND_SPEED": 343.0,
            "ARENA_WIDTH": 100.0,
            "ARENA_LENGTH": 100.0,
            "CALL_DIRECTIONALITY": 0.5,
            "AIR_ABSORPTION": 0.01,
            "CALL_DURATION": 0.1,
            "HEARING_THRESHOLD": 20.0,
            "EMITTED_SPL": 100.0,
            "REFLECTION_LOSS_WALL": 10.0,
            "REFLECTION_LOSS": 5.0,
        }

        # Mock origin and direction vectors
        self.origin = MagicMock()
        self.origin.distance_to.return_value = 0.0
        self.direction_vector = MagicMock()
        self.direction_vector.angle_between.return_value = 0.0

        # Create test DirectSound
        self.direct_sound = DirectSound(
            parameters_df=self.parameters_df,
            origin=self.origin,
            creation_time=0.0,
            emitter_id="test_emitter",
            direction_vector=self.direction_vector,
        )

    def test_initialization(self):
        """Test DirectSound initialization"""
        self.assertEqual(self.direct_sound.origin, self.origin)
        self.assertEqual(self.direct_sound.creation_time, 0.0)
        self.assertEqual(self.direct_sound.emitter_id, "test_emitter")
        self.assertEqual(self.direct_sound.initial_spl, 100.0)
        self.assertEqual(self.direct_sound.current_spl, 100.0)
        self.assertEqual(self.direct_sound.current_radius, 0)
        self.assertTrue(self.direct_sound.active)
        self.assertIsNone(self.direct_sound.reflected_from)
        self.assertEqual(self.direct_sound.wall_id, None)
        self.assertEqual(len(self.direct_sound.reflected_obstacles), 0)

    def test_create_echo(self):
        """Test echo creation"""
        # Mock point and normal vector
        point = MagicMock()
        point.distance_to.return_value = 10.0
        normal = MagicMock()
        self.origin.distance_to.return_value = 10.0
        # Test with wall reflection
        echo = self.direct_sound.create_echo(
            point=point, current_time=1.0, normal=normal, reflected_from="wall1"
        )

        self.assertIsNotNone(echo)
        self.assertIsInstance(echo, EchoSound)
        self.assertEqual(echo.origin, point)
        self.assertEqual(echo.creation_time, 1.0)
        self.assertEqual(echo.emitter_id, "test_emitter")
        self.assertEqual(echo.reflected_from, "wall1")
        self.assertEqual(echo.direction_vector, normal)
        self.assertEqual(echo.call_directionality, 0)  # Wall echoes are omnidirectional

        # Verify SPL calculation
        angle = self.direction_vector.angle_between(point)
        directionality = call_directionality_factor(a=0.5, theta=angle)
        distance_effect = 20 * math.log10(10.0)
        air_absorption = 0.01 * 10.0
        reflection_loss = 10.0  # Wall reflection loss
        expected_spl = (
            100.0 - distance_effect - air_absorption - reflection_loss + directionality
        )
        self.assertAlmostEqual(echo.initial_spl, expected_spl, places=2)

        # Test with non-wall reflection
        echo = self.direct_sound.create_echo(
            point=point, current_time=1.0, normal=normal, reflected_from="obj1"
        )
        self.assertEqual(echo.call_directionality, 0.5)  # Non-wall keeps directionality
        reflection_loss = 5.0  # Non-wall reflection loss
        expected_spl = (
            100.0 - distance_effect - air_absorption - reflection_loss + directionality
        )
        self.assertAlmostEqual(echo.initial_spl, expected_spl, places=2)

        # Test when SPL is below threshold
        # Mock a very negative directionality factor
        self.direct_sound.parameters_df["CALL_DIRECTIONALITY"] = 700
        self.direction_vector.angle_between.return_value = 30
        echo = self.direct_sound.create_echo(
            point=point, current_time=1.0, normal=normal, reflected_from="wall1"
        )
        self.assertIsNone(echo)

    def test_repr(self):
        """Test string representation"""
        repr_str = repr(self.direct_sound)
        self.assertIn("DirectSound", repr_str)
        self.assertIn("origin=", repr_str)
        self.assertIn("direction=", repr_str)
        self.assertIn("radius=", repr_str)
        self.assertIn("spl=", repr_str)
        self.assertIn("emitter=", repr_str)
        self.assertIn("creation_time=", repr_str)


if __name__ == "__main__":
    unittest.main()

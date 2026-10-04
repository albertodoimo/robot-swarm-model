import random
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.extend(
    [
        "./src/bat-swarm-model/",
        "./src/bat-swarm-model/core/",
        "./src/bat-swarm-model/plot/",
    ]
)
import numpy as np
from agents.class_jammers import Jammers  # Assuming this is the correct import path
from agents.class_sounds import DirectSound


class TestJammersInitialization(unittest.TestCase):
    """Tests for Jammers class initialization"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_parameters_df = {
            "TIME_STEP": 0.001,
            "NOISE_IN_CALL_RATE": 0.05,
        }
        self.position = Mock()
        self.position.x = 5.0
        self.position.y = 5.0
        self.direction = Mock()
        self.direction.normalize.return_value = Mock()
        self.direction.normalize.return_value.x = 1.0
        self.direction.normalize.return_value.y = 0.0
        self.call_rate = 10.0

    def test_initialization_with_random_position(self):
        """Test initialization with random position"""
        with patch("random.uniform") as mock_uniform:
            # Mock the random.uniform call in __init__
            mock_uniform.side_effect = [0.05]
            Jammers._id_counter = 0
            jammer = Jammers(
                self.mock_parameters_df, self.position, self.direction, self.call_rate
            )

            # Verify basic attributes
            self.assertEqual(jammer.id, 0)
            self.assertEqual(jammer.position, self.position)
            self.assertEqual(jammer.direction, self.direction.normalize.return_value)
            self.assertEqual(jammer.radius, 0.125)
            self.assertEqual(jammer.call_rate, self.call_rate)
            self.assertEqual(jammer.wall_id, None)

            # Verify time_since_last_call was set correctly
            self.assertEqual(jammer.time_since_last_call, 0.05)

            # Verify emit_times was initialized
            self.assertEqual(jammer.emit_times, [])

    def test_initialization_with_wall_id(self):
        """Test initialization with wall_id parameter"""
        jammer = Jammers(
            self.mock_parameters_df,
            self.position,
            self.direction,
            self.call_rate,
            wall_id=5,
        )

        self.assertEqual(jammer.wall_id, 5)

    def test_id_counter_increments(self):
        """Test that ID counter increments properly"""
        Jammers._id_counter = 0
        jammer1 = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )
        jammer2 = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )
        jammer3 = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )

        self.assertEqual(jammer1.id, 0)
        self.assertEqual(jammer2.id, 1)
        self.assertEqual(jammer3.id, 2)

    def test_id_counter_reset(self):
        """Test that ID counter can be reset"""
        jammer1 = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )
        jammer2 = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )

        # Reset the counter
        Jammers._id_counter = 0

        jammer3 = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )

        self.assertEqual(jammer3.id, 0)

    def test_initialization_with_different_call_rates(self):
        """Test initialization with different call rates"""
        for call_rate in [5.0, 10.0, 20.0]:
            with patch("random.uniform") as mock_uniform:
                mock_uniform.return_value = 0.1

                jammer = Jammers(
                    self.mock_parameters_df, self.position, self.direction, call_rate
                )

                self.assertEqual(jammer.call_rate, call_rate)
                self.assertEqual(jammer.time_since_last_call, 0.1)


class TestJammersUpdate(unittest.TestCase):
    """Tests for the update method"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_parameters_df = {
            "TIME_STEP": 0.1,
            "NOISE_IN_CALL_RATE": 0.05,
        }
        self.position = Mock()
        self.position.x = 5.0
        self.position.y = 5.0
        self.direction = Mock()
        self.direction.normalize.return_value = Mock()
        self.direction.normalize.return_value.x = 1.0
        self.direction.normalize.return_value.y = 0.0
        self.call_rate = 10.0

    def test_update_calls_emit_sounds(self):
        """Test that update calls emit_sounds"""
        jammer = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )

        # Mock emit_sounds to verify it's called
        with patch.object(jammer, "emit_sounds") as mock_emit_sounds:
            jammer.update(1.0, [])
            mock_emit_sounds.assert_called_once_with(1.0, [])

    def test_update_with_sound_objects(self):
        """Test update with existing sound objects"""
        jammer = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )

        # Create mock sound objects
        sound1 = Mock()
        sound2 = Mock()
        sound_objects = [sound1, sound2]

        # Mock emit_sounds to verify it's called with correct arguments
        with patch.object(jammer, "emit_sounds") as mock_emit_sounds:
            jammer.update(1.0, sound_objects)
            mock_emit_sounds.assert_called_once_with(1.0, sound_objects)


class TestJammersEmitSounds(unittest.TestCase):
    """Tests for the emit_sounds method"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_parameters_df = {
            "TIME_STEP": 0.01,
            "NOISE_IN_CALL_RATE": 0.05,
            "EMITTED_SPL": 100,
            "SOUND_SPEED": 343,
            "ARENA_WIDTH": 5,
            "ARENA_LENGTH": 10,
            "CALL_DIRECTIONALITY": 7,
        }
        self.position = Mock()
        self.position.x = 5.0
        self.position.y = 5.0
        self.direction = Mock()
        self.direction.normalize.return_value = Mock()
        self.direction.normalize.return_value.x = 1.0
        self.direction.normalize.return_value.y = 0.0
        self.call_rate = 10.0

    def test_emit_sounds_when_interval_passed(self):
        """Test sound emission when call interval has passed"""
        jammer = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )

        # Set time_since_last_call to be greater than call interval
        jammer.time_since_last_call = 0.25  # > 0.1 (1/10.0)

        sound_objects = []
        current_time = 1.0

        # Mock DirectSound to verify it's created correctly
        with patch("agents.class_sounds.DirectSound") as mock_direct_sound:
            jammer.emit_sounds(current_time, sound_objects)

            # Verify DirectSound was created with correct arguments]

            # Check the parameters
            self.assertEqual(sound_objects[0].parameters_df, self.mock_parameters_df)
            self.assertEqual(sound_objects[0].origin, self.position)
            self.assertEqual(sound_objects[0].creation_time, current_time)
            self.assertEqual(sound_objects[0].emitter_id, jammer.id)
            self.assertEqual(
                sound_objects[0].direction_vector, self.direction.normalize.return_value
            )

            # Verify the sound was added to sound_objects
            self.assertEqual(len(sound_objects), 1)
            # Verify wall_id was set
            self.assertEqual(sound_objects[0].wall_id, jammer.wall_id)

            # Verify emit_times was updated
            self.assertEqual(jammer.emit_times, [current_time])

            # Verify time_since_last_call was reset with noise
            self.assertLessEqual(jammer.time_since_last_call, 0.05)
            self.assertGreaterEqual(jammer.time_since_last_call, -0.05)

    def test_emit_sounds_when_interval_not_passed(self):
        """Test that no sound is emitted when call interval has not passed"""
        jammer = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )

        # Set time_since_last_call to be less than call interval
        jammer.time_since_last_call = 0.05  # < 0.1 (1/10.0)

        sound_objects = []
        current_time = 1.0

        # Mock DirectSound to verify it's not created
        with patch("agents.class_sounds.DirectSound") as mock_direct_sound:
            jammer.emit_sounds(current_time, sound_objects)

            # Verify DirectSound was not created
            mock_direct_sound.assert_not_called()

            # Verify no sound was added to sound_objects
            self.assertEqual(len(sound_objects), 0)

            # Verify emit_times was not updated
            self.assertEqual(jammer.emit_times, [])

            # Verify time_since_last_call was incremented
            self.assertAlmostEqual(jammer.time_since_last_call, 0.06)  # 0.05 + 0.1

    def test_emit_sounds_with_wall_id(self):
        """Test sound emission with wall_id set"""
        jammer = Jammers(
            self.mock_parameters_df,
            self.position,
            self.direction,
            self.call_rate,
            wall_id=5,
        )

        # Set time_since_last_call to be greater than call interval
        jammer.time_since_last_call = 0.2

        sound_objects = []

        # Mock DirectSound
        with patch("agents.class_sounds.DirectSound") as mock_direct_sound:
            jammer.emit_sounds(1.0, sound_objects)

            # Verify wall_id was set on the sound
            self.assertEqual(sound_objects[0].wall_id, 5)


class TestJammersRepr(unittest.TestCase):
    """Tests for the __repr__ method"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_parameters_df = {
            "TIME_STEP": 0.1,
            "NOISE_IN_CALL_RATE": 0.05,
        }
        self.position = Mock()
        self.position.x = 5.0
        self.position.y = 5.0
        self.direction = Mock()
        self.direction.normalize.return_value = Mock()
        self.direction.normalize.return_value.x = 1.0
        self.direction.normalize.return_value.y = 0.0
        self.call_rate = 10.0

    def test_repr(self):
        """Test the string representation of a jammer"""
        jammer = Jammers(
            self.mock_parameters_df, self.position, self.direction, self.call_rate
        )

        repr_str = repr(jammer)

        # Verify the format of the string representation
        self.assertIn("Jammer(id=", repr_str)
        self.assertIn("position=", repr_str)
        self.assertIn("direction=", repr_str)
        self.assertIn(f"id={jammer.id}", repr_str)


class TestJammersEdgeCases(unittest.TestCase):
    """Tests for edge cases in the Jammers class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_parameters_df = {
            "TIME_STEP": 0.1,
            "NOISE_IN_CALL_RATE": 0.05,
            "EMITTED_SPL": 100,
            "SOUND_SPEED": 343,
            "ARENA_WIDTH": 5,
            "ARENA_LENGTH": 10,
            "CALL_DIRECTIONALITY": 7,
        }
        self.position = Mock()
        self.position.x = 5.0
        self.position.y = 5.0
        self.direction = Mock()
        self.direction.normalize.return_value = Mock()
        self.direction.normalize.return_value.x = 1.0
        self.direction.normalize.return_value.y = 0.0

    def test_zero_call_rate(self):
        """Test jammer with zero call rate"""
        # This should cause division by zero in call_interval calculation
        with self.assertRaises(ZeroDivisionError):
            Jammers(self.mock_parameters_df, self.position, self.direction, 0.0)

    def test_very_high_call_rate(self):
        """Test jammer with very high call rate"""
        jammer = Jammers(self.mock_parameters_df, self.position, self.direction, 1000.0)

        # With high call rate, time_since_last_call should be very small
        self.assertLess(jammer.time_since_last_call, 0.001)

    def test_negative_noise_in_call_rate(self):
        """Test jammer with negative noise in call rate"""
        parameters = self.mock_parameters_df.copy()
        parameters["NOISE_IN_CALL_RATE"] = -0.1

        # This should work but might cause issues in emit_sounds
        jammer = Jammers(parameters, self.position, self.direction, 10.0)

        # Set time_since_last_call to be greater than call interval
        jammer.time_since_last_call = 0.2

        sound_objects = []

        # Mock DirectSound
        with patch("agents.class_sounds.DirectSound") as mock_direct_sound:
            jammer.emit_sounds(1.0, sound_objects)

            # Verify time_since_last_call was reset with negative noise
            # It should be between -0.1 and 0.1
            self.assertLessEqual(jammer.time_since_last_call, 0.1)
            self.assertGreaterEqual(jammer.time_since_last_call, -0.1)


# Add a simple test runner at the end
if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)

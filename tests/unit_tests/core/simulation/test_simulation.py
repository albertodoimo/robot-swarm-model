import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.extend(
    [
        "./src/bat-swarm-model/",
        "./src/bat-swarm-model/core/",
        "./src/bat-swarm-model/plot/",
    ]
)
from simulation.class_simulation import Simulation
from supporting_files.utilities import load_parameters

DIR_PARAMS = "./tests/unit_tests/params_unittest/test_bat_object.json"


class TestSimulation(unittest.TestCase):
    def test_init_creates_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = load_parameters(DIR_PARAMS)

            with patch("agents.class_bats.Bat"), patch(
                "agents.class_obstacles.Obstacle"
            ), patch("agents.make_walls.make_walls"), patch(
                "data_storage.handle_data_storage.handle_data_storage"
            ), patch(
                "supporting_files.utilities.read_temporal_masking_fn", return_value=[]
            ):

                Bat = Mock()
                Bat.return_value = Mock()
                Obstacle = Mock()
                Obstacle.return_value = Mock()

                sim = Simulation(cfg, tmpdir, use_hydra=False)

                self.assertTrue(os.path.exists(sim.output_dir))
                self.assertTrue(os.path.exists(sim.dir_to_store))

    def test_convert_necessary_information_into_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = load_parameters(DIR_PARAMS)

            with patch("agents.class_bats.Bat"), patch(
                "agents.class_obstacles.Obstacle"
            ), patch("agents.make_walls.make_walls"), patch(
                "data_storage.handle_data_storage.handle_data_storage"
            ), patch(
                "supporting_files.utilities.read_temporal_masking_fn", return_value=[]
            ), patch(
                "scores.polarization_score.compute_polarization", return_value=0.5
            ), patch(
                "scores.local_polarization_score.compute_local_polarization",
                return_value=0.3,
            ), patch(
                "scores.milling_score.compute_milling", return_value=0.2
            ):

                # Create mock bats
                bat1 = Mock()
                bat1.direction = Mock()
                bat1.direction.normalize.return_value = Mock()
                bat1.direction.normalize.return_value.x = 1.0
                bat1.direction.normalize.return_value.y = 0.0
                bat1.position = Mock()
                bat1.position.x = 0.0
                bat1.position.y = 0.0
                bat1.emit_times = [0]
                bat1.next_direction = Mock()
                bat1.next_direction.x = 1.0
                bat1.next_direction.y = 0.0
                bat1.next_direction.angle_between.return_value = 0.0
                bat1.direction.angle_between.return_value = 0.0
                bat1.response_type = "test"
                bat1.ipi_matrix_for_consistency = []
                bat1.memory_window_sum_matrix = []
                bat1.ipi_matrix_for_sensory_volume = []

                bat2 = Mock()
                bat2.direction = Mock()
                bat2.direction.normalize.return_value = Mock()
                bat2.direction.normalize.return_value.x = 1.0
                bat2.direction.normalize.return_value.y = 0.0
                bat2.position = Mock()
                bat2.position.x = 1.0
                bat2.position.y = 1.0
                bat2.emit_times = [0.1]
                bat2.next_direction = Mock()
                bat2.next_direction.x = 1.0
                bat2.next_direction.y = 0.0
                bat2.next_direction.angle_between.return_value = 0.0
                bat2.direction.angle_between.return_value = 0.0
                bat2.response_type = "test"
                bat2.ipi_matrix_for_consistency = []
                bat2.memory_window_sum_matrix = []
                bat2.ipi_matrix_for_sensory_volume = []

                Bat = Mock()
                Bat.return_value = Mock()
                Obstacle = Mock()
                Obstacle.return_value = Mock()
                Bat.return_value = bat1
                Bat.side_effect = [bat1, bat2]
                Obstacle.return_value = Mock()

                sim = Simulation(cfg, tmpdir, use_hydra=False)
                sim.time_elapsed = 0.5
                sim.sound_objects = []
                sim.jammers = []

                result = sim.convert_necessary_information_into_dict()

                self.assertIn("time", result)
                self.assertIn("bat_positions", result)
                self.assertIn("bat_directions", result)
                self.assertIn("polarization_score", result)
                self.assertIn("milling_score", result)


if __name__ == "__main__":
    unittest.main()

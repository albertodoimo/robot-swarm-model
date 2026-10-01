"""
Tests for the Simulation class in src/bat_swarm_model/core/simulation.py
"""

import os
import pickle
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

# Mock external dependencies before importing Simulation
sys_mock = Mock()
sys_mock.path = Mock()
sys_mock.path.append = Mock()
sys_mock.argv = ["test"]
sys_mock.exc_info = Mock(return_value=(None, None, None))
sys_mock.exit = Mock()

# Mock other external modules
with patch.dict(
    "sys.modules",
    {
        "hydra": Mock(),
        "numpy": np,
        "tqdm.rich": Mock(),
        "agents.class_bats": Mock(),
        "agents.class_obstacles": Mock(),
        "agents.class_sounds": Mock(),
        "agents.make_walls": Mock(),
        "data_storage.handle_data_storage": Mock(),
        "scores.local_polarization_score": Mock(),
        "scores.milling_score": Mock(),
        "scores.polarization_score": Mock(),
        "supporting_files.handle_reflections": Mock(),
        "supporting_files.utilities": Mock(),
        "supporting_files.vectors": Mock(),
    },
):
    import sys

    from agents.class_bats import Bat
    from agents.class_obstacles import Obstacle
    from agents.class_sounds import DirectSound
    from simulation import Simulation, cfg_to_flat_dict
    from supporting_files.vectors import Vector


class TestCfgToFlatDict:
    """Tests for the cfg_to_flat_dict helper function"""

    def test_cfg_to_flat_dict_with_nested_dict(self):
        """Test converting a nested config to flat dictionary"""
        # Create a mock config object
        mock_cfg = Mock()
        mock_cfg.group1 = {"param1": 1, "param2": 2}
        mock_cfg.group2 = {"param3": 3}

        # Mock OmegaConf methods
        with patch("simulation.OmegaConf") as mock_omega:
            mock_omega.to_container.return_value = {
                "group1": {"param1": 1, "param2": 2},
                "group2": {"param3": 3},
            }

            result = cfg_to_flat_dict(mock_cfg)

            assert result == {"param1": 1, "param2": 2, "param3": 3}
            mock_omega.to_container.assert_called_once_with(mock_cfg, resolve=True)


class TestSimulationInitialization:
    """Tests for Simulation class initialization"""

    @pytest.fixture
    def mock_cfg(self):
        """Create a mock configuration dictionary"""
        return {
            "NUM_BATS": 3,
            "OBSTACLE_COUNT": 2,
            "OBSTACLE_RADIUS": 1.0,
            "SIM_DURATION": 10.0,
            "TIME_STEP": 0.1,
            "OUTPUT_DIR_FOR_SIMULATION": "/tmp/test_simulation",
            "TEMPORAL_MASKING_FN_TYPE": "full",
            "HEARING_THRESHOLD": 0.1,
        }

    @pytest.fixture
    def mock_output_dir(self):
        """Create a temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_initialization_with_mock_config(self, mock_cfg, mock_output_dir):
        """Test basic initialization of Simulation class"""
        # Mock the external dependencies
        with patch("simulation.Bat"), patch("simulation.Obstacle"), patch(
            "simulation.make_walls"
        ), patch("simulation.handle_data_storage"), patch(
            "simulation.read_temporal_masking_fn", return_value=[]
        ):

            # Set up class mocks
            mock_bat_instance = Mock()
            mock_bat_instance.allocentric_axis_y = Mock()
            mock_bat_instance.direction = Mock()
            mock_bat_instance.direction.normalize.return_value = Mock()
            mock_bat_instance.direction.normalize.return_value.x = 1
            mock_bat_instance.direction.normalize.return_value.y = 0
            mock_bat_instance.position = Mock()
            mock_bat_instance.position.x = 0
            mock_bat_instance.position.y = 0
            mock_bat_instance.emit_times = [0]
            mock_bat_instance.next_direction = Mock()
            mock_bat_instance.next_direction.x = 0
            mock_bat_instance.next_direction.y = 1
            mock_bat_instance.next_direction.angle_between.return_value = 0
            mock_bat_instance.direction.angle_between.return_value = 0
            mock_bat_instance.response_type = "test"
            mock_bat_instance.ipi_matrix_for_consistency = []
            mock_bat_instance.memory_window_sum_matrix = []
            mock_bat_instance.ipi_matrix_for_sensory_volume = []

            Bat.return_value = mock_bat_instance

            mock_obstacle_instance = Mock()
            Obstacle.return_value = mock_obstacle_instance

            # Mock Vector class
            with patch("simulation.Vector") as mock_vector:
                mock_vector.return_value = Mock()
                mock_vector.return_value.x = 1
                mock_vector.return_value.y = 0

                # Initialize simulation
                sim = Simulation(mock_cfg, mock_output_dir, use_hydra=False)

                # Verify initialization
                assert sim.parameters_df == mock_cfg
                assert sim.output_dir == mock_output_dir + "/"
                assert len(sim.bats) == 3
                assert len(sim.obstacles) == 2
                assert sim.time_elapsed == 0.0
                assert len(sim.history) == 1  # Initial snapshot added in __init__

    def test_initialization_creates_output_directories(self, mock_cfg, mock_output_dir):
        """Test that initialization creates output directories"""
        with patch("simulation.Bat"), patch("simulation.Obstacle"), patch(
            "simulation.make_walls"
        ), patch("simulation.handle_data_storage"), patch(
            "simulation.read_temporal_masking_fn", return_value=[]
        ):

            # Mock Bat and Obstacle to avoid actual instantiation
            Bat.return_value = Mock()
            Obstacle.return_value = Mock()

            # Initialize simulation
            sim = Simulation(mock_cfg, mock_output_dir, use_hydra=False)

            # Verify directories were created
            assert os.path.exists(sim.output_dir)
            assert os.path.exists(sim.dir_to_store)


class TestSimulationRun:
    """Tests for the Simulation.run() method"""

    @pytest.fixture
    def mock_cfg(self):
        """Create a mock configuration dictionary"""
        return {
            "NUM_BATS": 2,
            "OBSTACLE_COUNT": 1,
            "OBSTACLE_RADIUS": 1.0,
            "SIM_DURATION": 1.0,  # Short duration for testing
            "TIME_STEP": 0.1,
            "OUTPUT_DIR_FOR_SIMULATION": "/tmp/test_simulation",
            "TEMPORAL_MASKING_FN_TYPE": "full",
            "HEARING_THRESHOLD": 0.1,
        }

    @pytest.fixture
    def mock_output_dir(self):
        """Create a temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_run_method_with_mock_dependencies(self, mock_cfg, mock_output_dir):
        """Test the run method with mocked dependencies"""
        with patch("simulation.Bat"), patch("simulation.Obstacle"), patch(
            "simulation.make_walls"
        ), patch("simulation.handle_data_storage"), patch(
            "simulation.read_temporal_masking_fn", return_value=[]
        ), patch(
            "simulation.handle_reflections", return_value=[]
        ), patch(
            "simulation.compute_polarization", return_value=0.5
        ), patch(
            "simulation.compute_local_polarization", return_value=0.3
        ), patch(
            "simulation.compute_milling", return_value=0.2
        ), patch(
            "simulation.pkl.dump"
        ), patch(
            "simulation.pkl.load", return_value=[]
        ), patch(
            "simulation.tqdm.rich.tqdm"
        ) as mock_tqdm, patch(
            "simulation.np"
        ) as mock_np, patch(
            "simulation.datetime"
        ) as mock_datetime:

            # Setup mocks
            mock_tqdm.return_value = [0.1, 0.2, 0.3]  # Time steps

            # Mock numpy functions
            mock_np.round.return_value = [0.1, 0.2, 0.3]
            mock_np.arange.return_value = [0.1, 0.2, 0.3]
            mock_np.mean.return_value = 0.5

            # Mock datetime
            mock_datetime.now.return_value = datetime(2023, 1, 1)

            # Mock Bat instances
            bat_mock = Mock()
            bat_mock.allocentric_axis_y = Mock()
            bat_mock.direction = Mock()
            bat_mock.direction.normalize.return_value = Mock()
            bat_mock.direction.normalize.return_value.x = 1
            bat_mock.direction.normalize.return_value.y = 0
            bat_mock.position = Mock()
            bat_mock.position.x = 0
            bat_mock.position.y = 0
            bat_mock.emit_times = [0]
            bat_mock.next_direction = Mock()
            bat_mock.next_direction.x = 0
            bat_mock.next_direction.y = 1
            bat_mock.next_direction.angle_between.return_value = 0
            bat_mock.direction.angle_between.return_value = 0
            bat_mock.response_type = "test"
            bat_mock.ipi_matrix_for_consistency = []
            bat_mock.memory_window_sum_matrix = []
            bat_mock.ipi_matrix_for_sensory_volume = []

            Bat.return_value = bat_mock

            # Mock Obstacle instances
            Obstacle.return_value = Mock()

            # Initialize simulation
            sim = Simulation(mock_cfg, mock_output_dir, use_hydra=False)

            # Mock the sound objects
            sim.sound_objects = []

            # Run the simulation
            sim.run()

            # Verify key interactions
            assert len(sim.history) > 1  # History should have initial + time steps
            assert bat_mock.update.called  # Bat update should be called
            assert sim.handle_reflections.called  # Reflections should be handled


class TestSimulationConvertNecessaryInformationIntoDict:
    """Tests for the convert_necessary_information_into_dict method"""

    @pytest.fixture
    def mock_cfg(self):
        """Create a mock configuration dictionary"""
        return {
            "NUM_BATS": 2,
            "OBSTACLE_COUNT": 1,
            "OBSTACLE_RADIUS": 1.0,
            "SIM_DURATION": 1.0,
            "TIME_STEP": 0.1,
            "OUTPUT_DIR_FOR_SIMULATION": "/tmp/test_simulation",
            "TEMPORAL_MASKING_FN_TYPE": "full",
            "HEARING_THRESHOLD": 0.1,
        }

    @pytest.fixture
    def mock_output_dir(self):
        """Create a temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_convert_necessary_information_into_dict(self, mock_cfg, mock_output_dir):
        """Test the convert_necessary_information_into_dict method"""
        with patch("simulation.Bat"), patch("simulation.Obstacle"), patch(
            "simulation.make_walls"
        ), patch("simulation.handle_data_storage"), patch(
            "simulation.read_temporal_masking_fn", return_value=[]
        ), patch(
            "simulation.compute_polarization", return_value=0.5
        ), patch(
            "simulation.compute_local_polarization", return_value=0.3
        ), patch(
            "simulation.compute_milling", return_value=0.2
        ):

            # Mock Bat instances
            bat1 = Mock()
            bat1.direction = Mock()
            bat1.direction.normalize.return_value = Mock()
            bat1.direction.normalize.return_value.x = 1
            bat1.direction.normalize.return_value.y = 0
            bat1.position = Mock()
            bat1.position.x = 0
            bat1.position.y = 0
            bat1.emit_times = [0]
            bat1.next_direction = Mock()
            bat1.next_direction.x = 0
            bat1.next_direction.y = 1
            bat1.next_direction.angle_between.return_value = 0
            bat1.direction.angle_between.return_value = 0
            bat1.response_type = "test"
            bat1.ipi_matrix_for_consistency = []
            bat1.memory_window_sum_matrix = []
            bat1.ipi_matrix_for_sensory_volume = []

            bat2 = Mock()
            bat2.direction = Mock()
            bat2.direction.normalize.return_value = Mock()
            bat2.direction.normalize.return_value.x = 1
            bat2.direction.normalize.return_value.y = 0
            bat2.position = Mock()
            bat2.position.x = 1
            bat2.position.y = 1
            bat2.emit_times = [0.1]
            bat2.next_direction = Mock()
            bat2.next_direction.x = 1
            bat2.next_direction.y = 0
            bat2.next_direction.angle_between.return_value = 0
            bat2.direction.angle_between.return_value = 0
            bat2.response_type = "test"
            bat2.ipi_matrix_for_consistency = []
            bat2.memory_window_sum_matrix = []
            bat2.ipi_matrix_for_sensory_volume = []

            Bat.return_value = bat1
            Bat.side_effect = [bat1, bat2]

            # Mock Obstacle instances
            Obstacle.return_value = Mock()

            # Initialize simulation
            sim = Simulation(mock_cfg, mock_output_dir, use_hydra=False)
            sim.time_elapsed = 0.5

            # Mock sound objects
            sim.sound_objects = []
            sim.jammers = []

            # Call the method
            result = sim.convert_necessary_information_into_dict()

            # Verify the result
            assert "time" in result
            assert "bat_ipi_counters" in result
            assert "bat_call_time" in result
            assert "bat_positions" in result
            assert "bat_directions" in result
            assert "sound_objects_count" in result
            assert "jammer_positions" in result
            assert "jammer_directions" in result
            assert "next_dir_angle" in result
            assert "current_dir_angle" in result
            assert "bat_response_vector" in result
            assert "response_type" in result
            assert "bat_ipi_matrix_for_consistency" in result
            assert "bat_sum_matrix" in result
            assert "bat_ipi_matrix_for_sensory_volume" in result
            assert "polarization_score" in result
            assert "local_polarization_score" in result
            assert "milling_score" in result


class TestSimulationHandleReflections:
    """Tests for the handle_reflections method"""

    @pytest.fixture
    def mock_cfg(self):
        """Create a mock configuration dictionary"""
        return {
            "NUM_BATS": 2,
            "OBSTACLE_COUNT": 1,
            "OBSTACLE_RADIUS": 1.0,
            "SIM_DURATION": 1.0,
            "TIME_STEP": 0.1,
            "OUTPUT_DIR_FOR_SIMULATION": "/tmp/test_simulation",
            "TEMPORAL_MASKING_FN_TYPE": "full",
            "HEARING_THRESHOLD": 0.1,
        }

    @pytest.fixture
    def mock_output_dir(self):
        """Create a temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_handle_reflections(self, mock_cfg, mock_output_dir):
        """Test the handle_reflections method"""
        with patch("simulation.Bat"), patch("simulation.Obstacle"), patch(
            "simulation.make_walls"
        ), patch("simulation.handle_data_storage"), patch(
            "simulation.read_temporal_masking_fn", return_value=[]
        ), patch(
            "simulation.handle_reflections", return_value=[Mock()]
        ) as mock_handle_reflections:

            # Mock Bat instances
            bat_mock = Mock()
            bat_mock.allocentric_axis_y = Mock()
            bat_mock.direction = Mock()
            bat_mock.direction.normalize.return_value = Mock()
            bat_mock.direction.normalize.return_value.x = 1
            bat_mock.direction.normalize.return_value.y = 0
            bat_mock.position = Mock()
            bat_mock.position.x = 0
            bat_mock.position.y = 0
            bat_mock.emit_times = [0]
            bat_mock.next_direction = Mock()
            bat_mock.next_direction.x = 0
            bat_mock.next_direction.y = 1
            bat_mock.next_direction.angle_between.return_value = 0
            bat_mock.direction.angle_between.return_value = 0
            bat_mock.response_type = "test"
            bat_mock.ipi_matrix_for_consistency = []
            bat_mock.memory_window_sum_matrix = []
            bat_mock.ipi_matrix_for_sensory_volume = []

            Bat.return_value = bat_mock

            # Mock Obstacle instances
            Obstacle.return_value = Mock()

            # Initialize simulation
            sim = Simulation(mock_cfg, mock_output_dir, use_hydra=False)

            # Set up sound objects
            sim.sound_objects = [Mock()]
            sim.wall_objects = [Mock()]
            sim.obstacles = [Mock()]
            sim.bats = [bat_mock]

            # Call the method
            sim.handle_reflections(0.5)

            # Verify handle_reflections was called with correct arguments
            mock_handle_reflections.assert_called_once()
            call_args = mock_handle_reflections.call_args
            assert call_args[0][0] == 0.5  # current_time
            assert call_args[0][1] == sim.sound_objects  # sound_objects
            assert call_args[0][2] == sim.wall_objects  # wall_objects
            assert call_args[0][3] == sim.obstacles  # obstacles
            assert call_args[0][4] == sim.bats  # bats


class TestSimulationSerializeSound:
    """Tests for the serialize_sound method"""

    @pytest.fixture
    def mock_cfg(self):
        """Create a mock configuration dictionary"""
        return {
            "NUM_BATS": 2,
            "OBSTACLE_COUNT": 1,
            "OBSTACLE_RADIUS": 1.0,
            "SIM_DURATION": 1.0,
            "TIME_STEP": 0.1,
            "OUTPUT_DIR_FOR_SIMULATION": "/tmp/test_simulation",
            "TEMPORAL_MASKING_FN_TYPE": "full",
            "HEARING_THRESHOLD": 0.1,
        }

    @pytest.fixture
    def mock_output_dir(self):
        """Create a temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_serialize_sound_direct(self, mock_cfg, mock_output_dir):
        """Test serializing a direct sound"""
        with patch("simulation.Bat"), patch("simulation.Obstacle"), patch(
            "simulation.make_walls"
        ), patch("simulation.handle_data_storage"), patch(
            "simulation.read_temporal_masking_fn", return_value=[]
        ):

            # Mock Bat instances
            bat_mock = Mock()
            bat_mock.allocentric_axis_y = Mock()
            bat_mock.direction = Mock()
            bat_mock.direction.normalize.return_value = Mock()
            bat_mock.direction.normalize.return_value.x = 1
            bat_mock.direction.normalize.return_value.y = 0
            bat_mock.position = Mock()
            bat_mock.position.x = 0
            bat_mock.position.y = 0
            bat_mock.emit_times = [0]
            bat_mock.next_direction = Mock()
            bat_mock.next_direction.x = 0
            bat_mock.next_direction.y = 1
            bat_mock.next_direction.angle_between.return_value = 0
            bat_mock.direction.angle_between.return_value = 0
            bat_mock.response_type = "test"
            bat_mock.ipi_matrix_for_consistency = []
            bat_mock.memory_window_sum_matrix = []
            bat_mock.ipi_matrix_for_sensory_volume = []

            Bat.return_value = bat_mock

            # Mock Obstacle instances
            Obstacle.return_value = Mock()

            # Initialize simulation
            sim = Simulation(mock_cfg, mock_output_dir, use_hydra=False)

            # Create a mock sound object
            sound = Mock()
            sound.origin = Mock()
            sound.origin.x = 0
            sound.origin.y = 0
            sound.current_radius = 1.0
            sound.current_spl = 0.5
            sound.emitter_id = 1
            sound.active = True

            # Mock the type of sound
            type(sound).type = "direct"

            # Call the method
            result = sim.serialize_sound(sound)

            # Verify the result
            assert result["origin"] == (0, 0)
            assert result["radius"] == 1.0
            assert result["spl"] == 0.5
            assert result["emitter_id"] == 1
            assert result["type"] == "direct"
            assert result["status"] == True


# Add more tests as needed for edge cases and error handling

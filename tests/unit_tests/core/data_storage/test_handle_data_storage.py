import sys

sys.path.extend(
    [
        "./src/bat-swarm-model/",
        "./src/bat-swarm-model/core/",
        "./src/bat-swarm-model/plot/",
    ]
)

import json
import pickle
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

# Replace 'your_module' with the actual module name where these functions are defined
from core.data_storage.handle_data_storage import (
    handle_data_storage,
    handle_data_storage_for_plotting,
    handle_data_storage_for_scoring,
)


class TestHandleDataStorage(unittest.TestCase):

    def setUp(self):
        """Set up test data and directory."""
        self.mock_parameters = {
            "CLEANUP_PLOT_DATA": 5,
            "OUTPUT_DIR_FOR_SIMULATION": "./tests/unit_tests/core/data_storage/test_output/",
        }
        self.output_dir = "./tests/unit_tests/core/data_storage/test_output/"
        Path(self.output_dir).mkdir(exist_ok=True)

    # def tearDown(self):
    #     """Clean up after tests."""
    #     for file in Path(self.output_dir).glob("*"):
    #         file.unlink()
    #     Path(self.output_dir).rmdir()

    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_scoring")
    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_plotting")
    def test_handle_data_storage_calls_both_functions(self, mock_plot, mock_scoring):
        """Test that handle_data_storage calls both scoring and plotting functions."""
        history = [{"time": 0.0}, {"time": 0.1}]
        handle_data_storage(0.1, False, history, self.mock_parameters, self.output_dir)

        mock_scoring.assert_called_once()
        mock_plot.assert_called_once()

    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_scoring")
    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_plotting")
    def test_handle_data_storage_clears_history_when_limit_reached(
        self, mock_plot, mock_scoring
    ):
        """Test that handle_data_storage returns True when history reaches limit."""
        history = [{} for _ in range(5)]  # Exactly at limit
        result = handle_data_storage(
            0.1, False, history, self.mock_parameters, self.output_dir
        )

        self.assertTrue(result)
        mock_scoring.assert_called()
        mock_plot.assert_called()

    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_scoring")
    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_plotting")
    def test_handle_data_storage_returns_false_when_below_limit(
        self, mock_plot, mock_scoring
    ):
        """Test that handle_data_storage returns False when below limit."""
        history = [{} for _ in range(3)]  # Below limit
        result = handle_data_storage(
            0.1, False, history, self.mock_parameters, self.output_dir
        )

        self.assertFalse(result)
        mock_scoring.assert_called()
        mock_plot.assert_called()

    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_scoring")
    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_plotting")
    def test_handle_data_storage_saves_parameters_at_end(self, mock_plot, mock_scoring):
        """Test that parameters are saved when is_end_of_code is True."""
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            handle_data_storage(0.0, True, [], self.mock_parameters, self.output_dir)

            mock_file.assert_any_call(
                "./tests/unit_tests/core/data_storage/test_output/parameters_used.json",
                "w",
                encoding="utf-8",
            )
            mock_file().write.assert_called()

    @patch("numpy.savez_compressed")
    def test_handle_data_storage_for_scoring_saves_compressed_numpy(self, mock_savez):
        """Test that handle_data_storage_for_scoring saves data in .npz format."""
        history = [
            {
                "time": 0.0,
                "bat_positions": [(0.0, 0.0), (1.0, 1.0)],
                "bat_directions": [(1.0, 0.0), (0.0, 1.0)],
            }
        ]
        handle_data_storage_for_scoring(
            0.0, True, history, self.mock_parameters, self.output_dir
        )

        mock_savez.assert_called_once()
        args, _ = mock_savez.call_args
        self.assertIn("times", args[0])
        self.assertIn("positions", args[0])
        self.assertIn("directions", args[0])

    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_scoring")
    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_plotting")
    def test_handle_data_storage_for_plotting_uses_pickle(
        self, mock_plot, mock_scoring
    ):
        """Test that handle_data_storage_for_plotting uses pickle."""
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            history = [{"time": 0.0}]
            handle_data_storage_for_plotting(
                0.0, True, history, self.mock_parameters, self.output_dir
            )

            mock_file.assert_any_call("test_output/history_dump_0.0000.pkl", "wb")
            mock_file().write.assert_called()

    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_scoring")
    @patch("core.data_storage.handle_data_storage.handle_data_storage_for_plotting")
    def test_handle_data_storage_does_not_save_if_plotting_disabled(
        self, mock_plot, mock_scoring
    ):
        """Test that no files are saved if store_data_for_plotting is False."""
        params = self.mock_parameters.copy()
        params["CLEANUP_PLOT_DATA"] = 5
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            handle_data_storage(
                0.0, True, [], params, self.output_dir, store_data_for_plotting=False
            )

            mock_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()

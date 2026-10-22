"""Add the saved simulation parameters to existing summary csv files.

Every job folder of a sweep/optimization run holds a parameters_used.json
(the parameters of that run) and a summary_dataframe_job_<job>_run<uuid>.csv
(one row of scores). This script appends every parameter from the json as a
column of the summary csv, so each row contains both the parameters and the
scores of a run. The csv is overwritten in place.

Columns already present in the csv are left untouched, so scores are never
overwritten and the script can safely be run more than once.

Usage (from the repository root):
    python src/robot-swarm-model/io/post_processing_sweepers/add_parameters_to_summary.py <results_dir>

If <results_dir> is not given, DEFAULT_RESULTS_DIR is used.
"""

import glob
import os
import sys

import pandas as pd
from tqdm.rich import tqdm

sys.path.extend(
    [
        "./src/robot-swarm-model/",
        "./src/robot-swarm-model/core/",
    ]
)

from supporting_files.utilities import load_parameters

DEFAULT_RESULTS_DIR = "/media/alberto/T7 Shield/Alberto Doimo/optimization_results"


def add_parameters_to_summary(results_dir):
    """Appends the parameters in parameters_used.json as columns to the
    summary_dataframe csv stored in the same job folder.

    Args:
        results_dir (string): directory containing one folder per job.
    """
    summary_files = glob.glob(results_dir + "/*/summary_dataframe_job_*.csv")
    missing_parameters = []

    for summary_file in tqdm(summary_files):
        job_dir = os.path.dirname(summary_file)
        parameter_file = job_dir + "/parameters_used.json"
        if not os.path.exists(parameter_file):
            missing_parameters.append(job_dir)
            continue

        parameters_df = load_parameters(parameter_file)
        summary_df = pd.read_csv(summary_file, index_col=0)

        # only add missing columns: re-running is safe and scores are never overwritten
        for key, value in parameters_df.items():
            if key not in summary_df.columns:
                summary_df[key] = value

        summary_df.to_csv(summary_file)

    print(f"updated {len(summary_files) - len(missing_parameters)} summary files")
    for job_dir in missing_parameters:
        print(f"no parameters_used.json in {job_dir}")


if __name__ == "__main__":
    results_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESULTS_DIR
    add_parameters_to_summary(results_dir)

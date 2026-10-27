"""Add the saved simulation parameters to existing summary csv files.

Every job folder of a sweep/optimization run holds a parameters_used.json
(the parameters of that run) and a summary_dataframe_job_<job>_run<uuid>.csv
(one row of scores). This script appends every parameter from the json as a
column of the summary csv, so each row contains both the parameters and the
scores of a run. The csv is overwritten in place.

Columns already present in the csv are left untouched, so scores are never
overwritten and the script can safely be run more than once.

Afterwards all summary csv files are merged into a single
results_dir/summary_all_jobs.csv (one header, one row per job).

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

DEFAULT_RESULTS_DIR = (
    "/media/alberto/T7 Shield/Alberto Doimo/optimization_results_2026_10_26"
)


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


def merge_summary_files(results_dir, output_file=None):
    """Merges the summary_dataframe csv of every job folder into one csv,
    keeping a single header (pd.concat as in
    https://stackoverflow.com/a/30335657).

    Args:
        results_dir (string): directory containing one folder per job.
        output_file (string, optional): path of the merged csv. Defaults to
            results_dir/summary_all_jobs.csv.

    Returns:
        DataFrame: merged summary, one row per job.
    """
    if output_file is None:
        output_file = results_dir + "/summary_all_jobs.csv"

    summary_files = glob.glob(results_dir + "/*/summary_dataframe_job_*.csv")
    complete_summaries = []
    incomplete_jobs = []
    for summary_file in summary_files:
        job_dir = os.path.dirname(summary_file)
        parameters_df = load_parameters(job_dir + "/parameters_used.json")
        summary_df = pd.read_csv(summary_file, index_col=0)

        # the run stops once DISTANCE_CAP is travelled: less means it did not finish
        if summary_df["distance travelled"].iloc[0] < parameters_df["DISTANCE_CAP"]:
            incomplete_jobs.append(job_dir)
            continue

        complete_summaries.append(summary_df)

    merged_df = pd.concat(complete_summaries, ignore_index=True)
    merged_df = merged_df.sort_values("job id", ignore_index=True)
    merged_df.to_csv(output_file, index=False)

    print(f"merged {len(complete_summaries)} summary files into {output_file}")
    for job_dir in incomplete_jobs:
        print(f"skipped, distance travelled < DISTANCE_CAP: {job_dir}")
    return merged_df


if __name__ == "__main__":
    results_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESULTS_DIR
    # add_parameters_to_summary(results_dir)
    merge_summary_files(results_dir)

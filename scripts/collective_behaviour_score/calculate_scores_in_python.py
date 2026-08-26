import os
import subprocess
import sys

import pandas as pd

sys.path.append("./scripts/collective_behaviour_score/")


def run_calculate_scores(
    input_csv,
    r_script="./scripts/collective_behaviour_score/swaRmverse_compute_score.R",
):
    out_dir = os.path.dirname(input_csv)
    subprocess.run(["Rscript", r_script, input_csv], check=True)
    g_metr = pd.read_parquet(os.path.join(out_dir, "g_metr.parquet"))
    pairwise = pd.read_parquet(os.path.join(out_dir, "pairwise.parquet"))
    return g_metr, pairwise


g_metr_1, pairwise_1 = run_calculate_scores(
    "/home/adityamoger/Documents/GitHub/bat-swarm-model/data/raw/testing_group_dynamics/4/swarmverse_data_19_08.csv"
)

import subprocess

import optuna

# NUM_BATS_VALUES = [4, 8]
# SEEDS = [1]
# LOUDNESS_TIME_DELAY_CAPS = [0.030, 0.050]
# ANGLE_RANGE_FOR_ATTRACTIONS = [30, 60, 90, 180]
# SPL_THRESHOLD_FOR_ATTRACTIONS = [75, 85, 95]
# SUSTAIN_SOUNDSS = [1, 3, 5]
# N_JOBS = 12


def main():
    subprocess.run(
        [
            "python",
            "./src/simulation/run_simulation_w_score_calcs.py",
            "--multirun",
            # f"arena.NUM_BATS={','.join(map(str, NUM_BATS_VALUES))}",
            # f"bat.LOUDNESS_TIME_DELAY_CAP={','.join(map(str, LOUDNESS_TIME_DELAY_CAPS))}",
            # f"bat.ANGLE_RANGE_FOR_ATTRACTION={','.join(map(str, ANGLE_RANGE_FOR_ATTRACTIONS))}",
            # f"bat.SPL_THRESHOLD_FOR_ATTRACTION={','.join(map(str, SPL_THRESHOLD_FOR_ATTRACTIONS))}",
            # f"bat.SUSTAIN_SOUNDS={','.join(map(str, SUSTAIN_SOUNDSS))}",
            # f"arena.seed={','.join(map(str, SEEDS))}",
            # f"hydra.launcher.n_jobs={N_JOBS}",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()

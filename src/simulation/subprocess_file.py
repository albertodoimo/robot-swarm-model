import subprocess

NUM_BATS_VALUES = [12]
SEEDS = [1]
LOUDNESS_TIME_DELAY_CAPS = [0.012, 0.030, 0.050]
ANGLE_RANGE_FOR_ATTRACTIONS = [180]
SPL_THRESHOLD_FOR_ATTRACTIONS = [75]
SUSTAIN_SOUNDSS = [5]
N_JOBS = 12


def main():
    subprocess.run(
        [
            "python",
            "./src/simulation/run_simulation.py",
            "-m",
            f"arena.NUM_BATS={','.join(map(str, NUM_BATS_VALUES))}",
            f"bat.LOUDNESS_TIME_DELAY_CAP={','.join(map(str, LOUDNESS_TIME_DELAY_CAPS))}",
            f"bat.ANGLE_RANGE_FOR_ATTRACTION={','.join(map(str, ANGLE_RANGE_FOR_ATTRACTIONS))}",
            f"bat.SPL_THRESHOLD_FOR_ATTRACTION={','.join(map(str, SPL_THRESHOLD_FOR_ATTRACTIONS))}",
            f"bat.SUSTAIN_SOUNDS={','.join(map(str, ANGLE_RANGE_FOR_ATTRACTIONS))}",
            f"arena.seed={','.join(map(str, SEEDS))}",
            f"hydra.launcher.n_jobs={N_JOBS}",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()

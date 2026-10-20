import subprocess

NUM_BATS_VALUES = [5, 10]
SEEDS = [5]
# LOUDNESS_TIME_DELAY_CAPS = [0.120]
ANGLE_RANGE_FOR_ATTRACTIONS = [20, 30]
ANGLE_RANGE_FOR_REPULSIONS = [60, 70, 80]
# CALL_RATES = [3, 4, 5]
BAT_ROTATION_SPEEDS = [300, 360]
EMITTED_SPL = [0, 95]

N_JOBS = 10


def main():
    subprocess.run(
        [
            "python",
            "./src/run_simulation/run_simulation_sweep.py",
            "-m",
            f"arena.NUM_BATS={','.join(map(str, NUM_BATS_VALUES))}",
            f"agents.sonoro.EMITTED_SPL={','.join(map(str, EMITTED_SPL))}",
            # f"agents.sonoro.LOUDNESS_TIME_DELAY_CAP={','.join(map(str, LOUDNESS_TIME_DELAY_CAPS))}",
            f"agents.sonoro.ANGLE_RANGE_FOR_ATTRACTION={','.join(map(str, ANGLE_RANGE_FOR_ATTRACTIONS))}",
            f"agents.sonoro.ANGLE_RANGE_FOR_REPULSION={','.join(map(str, ANGLE_RANGE_FOR_REPULSIONS))}",
            # f"agents.sonoro.CALL_RATE={','.join(map(str, CALL_RATES))}",
            f"agents.sonoro.BAT_ROTATION_SPEED={','.join(map(str, BAT_ROTATION_SPEEDS))}",
            f"arena.seed={','.join(map(str, SEEDS))}",
            f"hydra.launcher.n_jobs={N_JOBS}",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()

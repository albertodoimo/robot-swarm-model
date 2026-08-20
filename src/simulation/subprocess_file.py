import subprocess

NUM_BATS_VALUES = [1, 3]
SEEDS = [0, 3]
N_JOBS = 8


def main():
    subprocess.run(
        [
            "python",
            "./src/simulation/run_simulation.py",
            "-m",
            f"arena.NUM_BATS={','.join(map(str, NUM_BATS_VALUES))}",
            f"arena.seed={','.join(map(str, SEEDS))}",
            f"hydra.launcher.n_jobs={N_JOBS}",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()

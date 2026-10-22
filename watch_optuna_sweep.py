import os
import sys
import time
import optuna
from tqdm.rich import tqdm
from omegaconf import OmegaConf

CONFIG_PATH = "src/robot-swarm-model/core/config/optimization_config.yaml"


def watch_optuna_sweep():
    sweeper_cfg = OmegaConf.load(CONFIG_PATH).hydra.sweeper
    # only attach to an existing sweep: sqlite would silently create an empty db
    db_path = str(sweeper_cfg.storage).removeprefix("sqlite:///")
    if not os.path.exists(db_path):
        sys.exit(
            f"no sweep database at {os.path.abspath(db_path)}, start the sweep first"
        )
    study = optuna.load_study(
        study_name=str(sweeper_cfg.study_name),
        storage=str(sweeper_cfg.storage),
    )
    n_trials = int(sweeper_cfg.n_trials)

    with tqdm(total=n_trials, desc="trials") as bar:
        done = 0
        while done < n_trials:
            trials = study.get_trials(deepcopy=False)
            finished = sum(t.state.is_finished() for t in trials)
            running = sum(t.state == optuna.trial.TrialState.RUNNING for t in trials)
            bar.update(finished - done)
            bar.set_postfix(running=running)
            done = finished
            time.sleep(10)


if __name__ == "__main__":
    watch_optuna_sweep()

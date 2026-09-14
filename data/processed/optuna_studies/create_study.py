import optuna

optuna.create_study(
    study_name="multi-objective",
    storage="sqlite:///optuna_study.db",
    directions=["minimize", "minimize"],
    load_if_exists=True,
)
print("Study created/verified successfully.")

"""Plot the Pareto front of an optimization run from its merged summary csv
(see add_parameters_to_summary.py).

Objectives, as in run_simulation_for_optima.py:
    - interbat collision rate (collisions / SIM_DURATION), minimize
    - mean local polarization (range 1.0), maximize

Usage:
    python plot_pareto_from_csv.py [summary_all_jobs.csv]
or, to see the interactive plot inside VS Code: right click in the editor >
"Run Current File in Interactive Window" (or "Run Cell" above the # %% line).
"""

# %%

import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import seaborn as sns

# inside a Jupyter kernel (VS Code Interactive Window) show plotly inline
if "ipykernel" in sys.modules:
    pio.renderers.default = "vscode"

DEFAULT_SUMMARY_FILE = "/media/alberto/T7 Shield/Alberto Doimo/optimization_results_2026_10_26/summary_all_jobs.csv"
POLARIZATION_KEY = "mean local polarization, range 1.0"
GLOBAL_POLARIZATION_KEY = "mean polarization"
# scores (y) for the scores-vs-parameters plot: column name -> axis label
SCORES = {
    "normalized collision rate": "Collision rate (normalized 0-1)",
    POLARIZATION_KEY: "Local polarization (range 1.0)",
    GLOBAL_POLARIZATION_KEY: "Polarization",
}
SCORE_COLORS = ["#d62728", "#1f77b4", "#2ca02c"]
OPTIMIZED_PARAMETERS = [
    "CALL_RATE",
    "NUM_BATS",
    "BAT_SLOW_SPEED",
    "ANGLE_RANGE_FOR_REPULSION",
    "ANGLE_RANGE_FOR_ATTRACTION",
    "NOISE_IN_CALL_RATE",
    "ROTATION_CALL_RATE_PRODUCT",
]
# marker shape per CALL_RATE value (in increasing order); 3d supports only these
CALL_RATE_SYMBOLS = [
    "circle",
    "diamond",
    "square",
    "cross",
    "x",
    "circle-open",
    "diamond-open",
    "square-open",
]
# colour per NUM_BATS value (in increasing order)
NUM_BATS_COLORS = ["#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b"]


def plot_interactive_pareto(summary_df, pareto_df, output_file):
    """Interactive 3d Pareto plot (collision rate, local polarization, global
    polarization): marker shape = CALL_RATE, colour = NUM_BATS, Pareto points
    large and opaque, all other jobs small and faded. Hovering a point shows
    its job id and the optimized parameters. Saved as a standalone html file."""
    hover_columns = ["job id"] + OPTIMIZED_PARAMETERS
    hovertemplate = (
        "collision rate: %{x:.3f}<br>"
        "local polarization: %{y:.3f}<br>"
        "polarization: %{z:.3f}<br>"
        + "<br>".join(
            f"{column}: %{{customdata[{i}]}}" for i, column in enumerate(hover_columns)
        )
        + "<extra></extra>"
    )

    num_bats_values = sorted(summary_df["NUM_BATS"].unique())
    call_rate_values = sorted(summary_df["CALL_RATE"].unique())
    num_bats_colors = dict(zip(num_bats_values, NUM_BATS_COLORS))

    fig = go.Figure()
    # one trace per call rate (shape); colour per point from NUM_BATS
    for symbol, call_rate in zip(CALL_RATE_SYMBOLS, call_rate_values):
        for is_pareto in (False, True):
            subset = summary_df[
                (summary_df["CALL_RATE"] == call_rate)
                & (summary_df["pareto"] == is_pareto)
            ]
            if subset.empty:
                continue
            fig.add_trace(
                go.Scatter3d(
                    x=subset["collision rate"],
                    y=subset[POLARIZATION_KEY],
                    z=subset[GLOBAL_POLARIZATION_KEY],
                    mode="markers",
                    marker=dict(
                        size=4 if is_pareto else 3,
                        symbol=symbol,
                        color=subset["NUM_BATS"].map(num_bats_colors),
                    ),
                    opacity=1.0 if is_pareto else 0.6,
                    name=f"call rate {call_rate}",
                    legendgroup=f"call rate {call_rate}",
                    legendgrouptitle_text=(
                        "CALL_RATE (shape)"
                        if call_rate == call_rate_values[0]
                        else None
                    ),
                    showlegend=not is_pareto,
                    customdata=subset[hover_columns],
                    hovertemplate=hovertemplate,
                )
            )

    # legend-only entries for the NUM_BATS colours
    for num_bats in num_bats_values:
        fig.add_trace(
            go.Scatter3d(
                x=[None],
                y=[None],
                z=[None],
                mode="markers",
                marker=dict(size=4, color=num_bats_colors[num_bats]),
                name=f"{num_bats} robots",
                legendgroup="num bats",
                legendgrouptitle_text="NUM_BATS (colour)",
            )
        )

    # Pareto frontier: surface triangulated through the Pareto points
    if len(pareto_df) >= 3:
        fig.add_trace(
            go.Mesh3d(
                x=pareto_df["collision rate"],
                y=pareto_df[POLARIZATION_KEY],
                z=pareto_df[GLOBAL_POLARIZATION_KEY],
                color="red",
                opacity=0.2,
                hoverinfo="skip",
                name="Pareto frontier",
                showlegend=True,
            )
        )
    fig.update_layout(
        title="Pareto Front",
        scene=dict(
            xaxis_title="Interbat collision rate (collisions / s)",
            yaxis_title="Mean local polarization (range 1.0)",
            zaxis_title="Mean polarization",
        ),
        legend_title_text="",
    )
    fig.write_html(output_file)
    fig.show()


def plot_scores_vs_parameters(summary_df, pareto_df, output_file):
    """One subplot per optimized parameter, each with a box per score for
    every parameter value (box: 25-75th percentile and median, whiskers:
    10-90th percentile), every job as a point and a line through the mean.
    Saved as a pdf."""
    scores_long_df = summary_df.melt(
        id_vars=OPTIMIZED_PARAMETERS,
        value_vars=list(SCORES),
        var_name="score",
        value_name="value",
    )
    scores_long_df["score"] = scores_long_df["score"].map(SCORES)
    palette = dict(zip(SCORES.values(), SCORE_COLORS))
    box_width = 0.8

    fig, axes = plt.subplots(
        len(OPTIMIZED_PARAMETERS), 1, figsize=(12, 4 * len(OPTIMIZED_PARAMETERS))
    )
    for ax, parameter in zip(axes, OPTIMIZED_PARAMETERS):
        common = dict(
            data=scores_long_df,
            x=parameter,
            y="value",
            hue="score",
            hue_order=list(SCORES.values()),
            palette=palette,
            ax=ax,
        )
        sns.boxplot(
            **common,
            whis=(10, 90),
            width=box_width,
            showfliers=False,
            fill=False,
        )
        sns.stripplot(**common, dodge=True, size=2, alpha=0.4, legend=False)
        # dodge so the mean points sit on the centre of their box
        sns.pointplot(
            **common,
            estimator="mean",
            errorbar=None,
            dodge=box_width * (len(SCORES) - 1) / len(SCORES),
            markersize=4,
            linewidth=1.5,
            legend=False,
        )
        ax.set_xlabel(parameter)
        ax.set_ylabel("score")
        ax.legend(title="", loc="upper right")

    fig.suptitle("Scores vs optimized parameters")
    fig.tight_layout()
    fig.savefig(output_file, bbox_inches="tight")
    plt.show()


def pareto_mask(objectives):
    """True for every point not dominated by another one.

    Args:
        objectives (ndarray): (n_points, n_objectives), every objective to be
            minimized (negate the ones to maximize).
    """
    is_pareto = np.ones(len(objectives), dtype=bool)
    for i in range(len(objectives)):
        # j dominates i: no worse in every objective, better in at least one
        dominated_by = np.all(objectives <= objectives[i], axis=1) & np.any(
            objectives < objectives[i], axis=1
        )
        is_pareto[i] = not dominated_by.any()
    return is_pareto


if __name__ == "__main__":
    # in a Jupyter kernel sys.argv holds the kernel's own arguments, not a csv
    if len(sys.argv) > 1 and sys.argv[1].endswith(".csv"):
        summary_file = sys.argv[1]
    else:
        summary_file = DEFAULT_SUMMARY_FILE
    summary_df = pd.read_csv(summary_file)
    summary_df = summary_df.dropna(
        subset=["interbat collision total", POLARIZATION_KEY]
    )

    summary_df["collision rate"] = (
        summary_df["interbat collision total"] / summary_df["SIM_DURATION"]
    )
    # scaled to 0-1 by the worst job, to compare with the polarization scores
    summary_df["normalized collision rate"] = (
        summary_df["collision rate"] / summary_df["collision rate"].max()
    )
    collision = summary_df["collision rate"].to_numpy()
    polarization = summary_df[POLARIZATION_KEY].to_numpy()
    global_polarization = summary_df[GLOBAL_POLARIZATION_KEY].to_numpy()

    # 2d front (the two optimized objectives) for the static plot
    pareto_2d = pareto_mask(np.column_stack([collision, -polarization]))
    pareto_2d_df = summary_df[pareto_2d].sort_values("collision rate")

    # 3d front: minimize collision, maximize local and global polarization
    summary_df["pareto"] = pareto_mask(
        np.column_stack([collision, -polarization, -global_polarization])
    )
    pareto_df = summary_df[summary_df["pareto"]].sort_values("collision rate")

    print(
        pareto_df[
            ["job id", "collision rate", POLARIZATION_KEY, GLOBAL_POLARIZATION_KEY]
            + OPTIMIZED_PARAMETERS
        ].to_string(index=False)
    )
    pareto_df.to_csv(summary_file.replace(".csv", "_pareto.csv"), index=False)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(collision, polarization, alpha=0.4, color="gray", label="All jobs")
    ax.plot(
        pareto_2d_df["collision rate"],
        pareto_2d_df[POLARIZATION_KEY],
        "o-",
        color="red",
        label="Pareto front",
    )
    ax.set_xlabel("Interbat collision rate (collisions / s)")
    ax.set_ylabel("Mean local polarization (range 1.0)")
    ax.set_title("Pareto Front")
    ax.legend()
    ax.set_box_aspect(1)

    plt.savefig(
        summary_file.replace(".csv", "_pareto.pdf"), dpi=150, bbox_inches="tight"
    )
    # plt.show()

    plot_interactive_pareto(
        summary_df, pareto_df, summary_file.replace(".csv", "_pareto.html")
    )
    plot_scores_vs_parameters(
        summary_df,
        pareto_df,
        summary_file.replace(".csv", "_scores_vs_parameters.pdf"),
    )

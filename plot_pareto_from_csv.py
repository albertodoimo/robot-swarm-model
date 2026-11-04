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
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import seaborn as sns
from plotly.subplots import make_subplots

# inside a Jupyter kernel (VS Code Interactive Window) show plotly inline
if "ipykernel" in sys.modules:
    pio.renderers.default = "vscode"

# DEFAULT_SUMMARY_FILE = "/media/alberto/T7 Shield/Alberto Doimo/optimization_results_2026_10_26/summary_all_jobs.csv"
# DEFAULT_SUMMARY_FILE = "/media/alberto/T7 Shield/Alberto Doimo/simulation/optimization_results_2026_10_28/summary_all_jobs.csv"
DEFAULT_SUMMARY_FILE = "/home/alberto/Documents/ActiveSensingCollectives_lab/Swarm_simulation/robot-swarm-model/optimization_results_2026_10_28/summary_all_jobs_with_resume.csv"
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
# font size of all text in the per-group-size plot
TEXT_SIZE = 14


def plot_interactive_pareto(summary_df, pareto_df, output_file):
    """Interactive 3d Pareto plot (collision rate, local polarization, global
    polarization): marker shape = CALL_RATE, colour = NUM_BATS, Pareto points
    large and opaque, all other jobs small and faded. Hovering a point shows
    its job id and the optimized parameters. Saved as a standalone html file."""
    hover_columns = (
        ["job id"] + OPTIMIZED_PARAMETERS + ["duration (min)", "distance travelled"]
    )
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
        font=dict(size=TEXT_SIZE),
    )
    fig.write_html(output_file)
    fig.show()


def plot_pareto_per_group_size(summary_df, output_file):
    """One 3d Pareto plot per NUM_BATS value, side by side in one html file.
    Each Pareto front is computed only among the jobs with that group size
    (minimize collision rate, maximize local and global polarization).
    Marker shape = CALL_RATE, Pareto points large and opaque, all other jobs
    small and faded, red surface through the Pareto points. All panels share
    the same axis ranges. Hovering a point shows its job id and the optimized
    parameters."""
    hover_columns = (
        ["job id"] + OPTIMIZED_PARAMETERS + ["duration (min)", "distance travelled"]
    )
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
    call_rate_symbols = dict(zip(call_rate_values, CALL_RATE_SYMBOLS))

    fig = make_subplots(
        rows=1,
        cols=len(num_bats_values),
        specs=[[{"type": "scene"}] * len(num_bats_values)],
        subplot_titles=[f"{num_bats} robots" for num_bats in num_bats_values],
        horizontal_spacing=0.01,
    )
    for col, (color, num_bats) in enumerate(
        zip(NUM_BATS_COLORS, num_bats_values), start=1
    ):
        group_df = summary_df[summary_df["NUM_BATS"] == num_bats].copy()
        group_df["pareto"] = pareto_mask(
            np.column_stack(
                [
                    group_df["collision rate"],
                    -group_df[POLARIZATION_KEY],
                    -group_df[GLOBAL_POLARIZATION_KEY],
                ]
            )
        )

        for call_rate in call_rate_values:
            for is_pareto in (False, True):
                subset = group_df[
                    (group_df["CALL_RATE"] == call_rate)
                    & (group_df["pareto"] == is_pareto)
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
                            size=5 if is_pareto else 3,
                            symbol=call_rate_symbols[call_rate],
                            color=color,
                        ),
                        opacity=1.0 if is_pareto else 0.3,
                        name=f"call rate {call_rate}",
                        legendgroup=f"call rate {call_rate}",
                        showlegend=False,
                        customdata=subset[hover_columns],
                        hovertemplate=hovertemplate,
                    ),
                    row=1,
                    col=col,
                )

        # Pareto frontier of this group size
        pareto_df = group_df[group_df["pareto"]]
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
                    legendgroup="pareto frontier",
                    showlegend=(col == 1),
                ),
                row=1,
                col=col,
            )
        print(f"{num_bats} robots: {len(pareto_df)} Pareto jobs of {len(group_df)}")

    # legend-only entries for the CALL_RATE shapes
    for call_rate in call_rate_values:
        fig.add_trace(
            go.Scatter3d(
                x=[None],
                y=[None],
                z=[None],
                mode="markers",
                marker=dict(size=5, symbol=call_rate_symbols[call_rate], color="gray"),
                name=f"call rate {call_rate}",
                legendgroup=f"call rate {call_rate}",
                legendgrouptitle_text=(
                    "CALL_RATE (shape)" if call_rate == call_rate_values[0] else None
                ),
            ),
            row=1,
            col=1,
        )

    # same axes in every panel, so the group sizes can be compared
    scene = dict(
        xaxis=dict(
            title="Collision rate (collisions / s)",
            range=[0, summary_df["collision rate"].max()],
        ),
        yaxis=dict(
            title="Local polarization (range 1.0)",
            range=[
                summary_df[POLARIZATION_KEY].min(),
                summary_df[POLARIZATION_KEY].max(),
            ],
        ),
        zaxis=dict(
            title="Polarization",
            range=[
                summary_df[GLOBAL_POLARIZATION_KEY].min(),
                summary_df[GLOBAL_POLARIZATION_KEY].max(),
            ],
        ),
    )
    fig.update_scenes(scene)
    # subplot titles are annotations with their own font size
    fig.update_annotations(font_size=TEXT_SIZE)
    fig.update_layout(
        title="Pareto front per group size",
        # height=700,
        # width=700 * len(num_bats_values),
        legend_title_text="",
        font=dict(size=TEXT_SIZE),
    )
    fig.write_html(output_file)
    fig.show()


def plot_scores_vs_parameters(summary_df, pareto_df, output_file):
    """One subplot per optimized parameter, each a seaborn ridge plot with the
    scores on x and one ridge per parameter value on y: for every score its
    own ridge (violin cut to its upper half), every job as a jittered point
    below the ridge, and a line through the means. Saved as a pdf."""
    scores_long_df = summary_df.melt(
        id_vars=OPTIMIZED_PARAMETERS,
        value_vars=list(SCORES),
        var_name="score",
        value_name="value",
    )
    scores_long_df["score"] = scores_long_df["score"].map(SCORES)
    palette = dict(zip(SCORES.values(), SCORE_COLORS))
    # height taken by the ridges of one parameter value and by one score's
    # ridge; peak height of each ridge and offset of its points below it
    group_width = 0.9
    slot_width = group_width / len(SCORES)
    ridge_height = 0.8 * slot_width
    rain_offset = 0.12 * slot_width

    # grid with about as many columns as rows
    n_cols = int(np.ceil(np.sqrt(len(OPTIMIZED_PARAMETERS))))
    n_rows = int(np.ceil(len(OPTIMIZED_PARAMETERS) / n_cols))
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows), squeeze=False
    )
    axes = axes.flatten()
    for ax in axes[len(OPTIMIZED_PARAMETERS) :]:
        ax.set_visible(False)
    for ax, parameter in zip(axes, OPTIMIZED_PARAMETERS):
        # largest parameter value on top
        order = sorted(summary_df[parameter].unique(), reverse=True)
        common = dict(
            data=scores_long_df,
            x="value",
            y=parameter,
            order=order,
            hue="score",
            hue_order=list(SCORES.values()),
            palette=palette,
            orient="h",
            ax=ax,
            legend=False,
        )

        # ridges: one seaborn violin per score on its own baseline, cut to its
        # upper half and stretched to ridge_height (the categorical y axis
        # points down)
        n_collections = len(ax.collections)
        sns.violinplot(
            **common,
            width=group_width,
            cut=0,
            inner=None,
            density_norm="width",
            linewidth=0,
            alpha=0.3,
        )
        for body in ax.collections[n_collections:]:
            color = body.get_facecolor()[0][:3]
            for path in body.get_paths():
                y = path.vertices[:, 1]
                baseline = (y.min() + y.max()) / 2
                y = np.clip(y, -np.inf, baseline)
                path.vertices[:, 1] = baseline - (baseline - y) * ridge_height / (
                    baseline - y.min()
                )
                ax.hlines(baseline, 0, 1, color=color, linewidth=0.8)
            # outline in the ridge colour
            body.set_edgecolor(color)
            body.set_linewidth(1.2)

        # rain: every job, jittered just below its ridge
        n_collections = len(ax.collections)
        sns.stripplot(**common, dodge=True, jitter=0.02, size=2, alpha=0.4, linewidth=0)
        for points in ax.collections[n_collections:]:
            offsets = points.get_offsets()
            offsets[:, 1] += rain_offset
            points.set_offsets(offsets)

        # mean of each parameter value on its ridge's baseline, connected
        # across the parameter values
        sns.pointplot(
            **common,
            estimator="mean",
            errorbar=None,
            dodge=group_width - slot_width,
            markersize=3,
            linewidth=1.5,
        )

        # down to the last value's bottom slot, up to the first ridge's peak
        ax.set_ylim(len(order) - 0.5, -(group_width - slot_width) / 2 - ridge_height)
        ax.set_xlabel("score")
        ax.set_ylabel(parameter)
        # all scores range 0-1
        ax.set_xlim(0, 1)
        ax.tick_params(axis="y", length=0)
        sns.despine(ax=ax, left=True)

    # one legend for the whole figure
    handles = [Patch(color=color, alpha=0.6) for color in SCORE_COLORS]
    labels = list(SCORES.values())
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=len(SCORES),
        bbox_to_anchor=(0.5, 1.0),
        frameon=False,
    )

    fig.suptitle("Scores vs optimized parameters", y=1.03)
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
    # duration is saved in frames (one per TIME_STEP)
    summary_df["duration (min)"] = (
        summary_df["duration"] * summary_df["TIME_STEP"] / 60
    ).round(2)
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

    fig, ax = plt.subplots()
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
    plot_pareto_per_group_size(
        summary_df, summary_file.replace(".csv", "_pareto_per_group_size.html")
    )
    plot_scores_vs_parameters(
        summary_df,
        pareto_df,
        summary_file.replace(".csv", "_scores_vs_parameters.pdf"),
    )

"""Polarization & milling score line plot (position 0, 2).

Plots a rolling 1-second average of `polarization_score` and `milling_score`
(present in each frame's data dict). Both lines update every frame, like all
other animated panels, growing to show the full history up to the current
frame.
"""

import bisect

import matplotlib.pyplot as plt
from plotting.base_module import AnimationModule


class PolarizationMillingModule(AnimationModule):
    GRID_POS = (0, 2)
    PROJECTION = None

    def setup(self, history, **_):
        ax = self.ax

        self.times = [frame["time"] for frame in history]
        polarization_raw = [frame["polarization_score"] for frame in history]
        milling_raw = [frame["milling_score"] for frame in history]

        # Pre-compute rolling 1-second average for every frame in the history.
        # `self.times` is sorted ascending (guaranteed by stitch_together_history_lists),
        # so we can use bisect to find the start of the 1-second window efficiently.
        self.avg_polarization = []
        self.avg_milling = []
        window_seconds = 1.0

        for i, t in enumerate(self.times):
            start_idx = bisect.bisect_left(self.times, t - window_seconds)
            window_polarization = polarization_raw[start_idx : i + 1]
            window_milling = milling_raw[start_idx : i + 1]
            self.avg_polarization.append(
                sum(window_polarization) / len(window_polarization)
            )
            self.avg_milling.append(sum(window_milling) / len(window_milling))

        ax.set_title("Polarization & Milling Score (1s avg)")
        ax.set_xlim(self.times[0], self.times[-1])
        ax.set_ylim(0, 1)

        (self.polarization_line,) = ax.plot(
            [], [], color="cyan", linewidth=1.5, label="Polarization"
        )
        (self.milling_line,) = ax.plot(
            [], [], color="magenta", linewidth=1.5, label="Milling"
        )
        ax.legend(
            loc="upper right",
            fontsize=9,
            framealpha=0.3,
            facecolor="black",
            edgecolor="white",
        )

        return [self.polarization_line, self.milling_line]

    def init_frame(self):
        self.polarization_line.set_data([], [])
        self.milling_line.set_data([], [])
        return [self.polarization_line, self.milling_line]

    def update_frame(self, i, frame, context):
        self.polarization_line.set_data(
            self.times[: i + 1], self.avg_polarization[: i + 1]
        )
        self.milling_line.set_data(self.times[: i + 1], self.avg_milling[: i + 1])
        return [self.polarization_line, self.milling_line]

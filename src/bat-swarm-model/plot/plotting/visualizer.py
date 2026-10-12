"""Orchestrator: builds the figure, wires up whichever modules were chosen,
and drives the FuncAnimation loop exactly like the original `visualize()`.
"""

import sys

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from plotting.arena_module import ArenaModule
from plotting.common import stitch_together_history_lists
from plotting.info_text_module import InfoTextModule
from plotting.ipi_radial_module import IPIRadialModule
from plotting.polarization_milling_module import PolarizationMillingModule
from plotting.sensory_volume_module import SensoryVolumeModule
from plotting.sum_radial_module import SumRadialModule
from tqdm.rich import tqdm

# Original behaviour = every panel included.
DEFAULT_MODULES = [
    ArenaModule,
    IPIRadialModule,
    SumRadialModule,
    SensoryVolumeModule,
    InfoTextModule,
]

# Handy string aliases, e.g. modules=["arena", "sensory_volume"]

AVAILABLE_MODULES = {
    "arena": ArenaModule,
    "ipi_radial": IPIRadialModule,
    "sum_radial": SumRadialModule,
    "sensory_volume": SensoryVolumeModule,
    "info_text": InfoTextModule,
    "polarization_milling": PolarizationMillingModule,  # <-- new
}


def _resolve_module(m):
    if isinstance(m, str):
        return AVAILABLE_MODULES[m]()
    if isinstance(m, type):
        return m()
    return m  # already an instance, e.g. ArenaModule(grid_pos=(0, 0))


def visualize(
    output_dir,
    save_animation,
    unique_id,
    resolution,
    show_sounds,
    focal_bat,
    modules=None,
    rows=2,
    columns=3,
):
    """Builds (and optionally saves) an animation made of the requested modules.

    Args:
        modules (list, optional): list of module classes / instances / string
            aliases (see AVAILABLE_MODULES) to include. Defaults to every
            panel the original script hard-coded.
    """

    if modules is None:
        modules = DEFAULT_MODULES

    module_instances = [_resolve_module(m) for m in modules]

    history, parameters_df, bats, obstacles, jammers = stitch_together_history_lists(
        output_dir
    )
    history = history[::resolution]

    fig = plt.figure(figsize=(16, 9))

    gridspec = GridSpec(rows, columns, figure=fig)

    for module in module_instances:
        if module.GRID_POS is not None:
            module.add_axis(fig, gridspec)
        else:
            module.add_axis(fig, gridspec)  # InfoTextModule overrides -> no-op

    context = dict(
        parameters_df=parameters_df,
        bats=bats,
        obstacles=obstacles,
        jammers=jammers,
        history=history,
        focal_bat=focal_bat,
        show_sounds=show_sounds,
        resolution=resolution,
    )

    for module in module_instances:
        module.setup(**context)

    def init():
        artists = []
        for module in module_instances:
            artists += module.init_frame()
        return artists

    def animate(i):
        frame = history[i]
        artists = []
        for module in module_instances:
            artists += module.update_frame(i, frame, context)
        print(artists)
        return artists

    frames = tqdm(range(len(history)), file=sys.stdout, desc="Animating")

    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=frames,
        init_func=init,
        blit=False,
        interval=parameters_df["FRAME_RATE"] * 0.00001,
    )

    print(len(history))
    arena_module = next(
        (m for m in module_instances if isinstance(m, ArenaModule)), None
    )
    if arena_module is not None:
        handles, labels = arena_module.get_legend_handles()
        print(labels)
        arena_module.ax.legend(
            loc="center right", bbox_to_anchor=(-0.1, 0.5), handles=handles
        )

    #     arena_module = next(
    #         (m for m in module_instances if isinstance(m, ArenaModule)), None
    #     )
    # if arena_module is not None:
    #     handles, labels = arena_module.get_legend_handles()
    #     print(labels)
    #     plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), handles=handles)

    if save_animation:
        ffwriter = animation.FFMpegWriter(fps=parameters_df["FRAME_RATE"])
        ani.save(
            save_animation + f"/animation_without_sound_id_{unique_id}.mp4",
            writer=ffwriter,
        )
    plt.show()

import logging
from typing import NamedTuple, List
import matplotlib.pyplot as plt
import numpy as np
import treefiles as tf
from eulerian_magnification.io import load_video_float
from matplotlib.animation import FuncAnimation, PillowWriter
from benchmark import apply_multiple_evms

class Param(NamedTuple):
    name: str
    values: List[float]


def main(x: Param, y: Param, videos, final_filename):
    fig, axs = prepare_canvas(x, y, figsize=(6, 6))
    nx, ny = len(x.values), len(y.values)
    set_labels(x, y, axs)

    # Passage du RGB au BGR
    for n in range(len(videos)):
        videos[n] = videos[n][..., ::-1]

    nb_frames, dim_y, dim_x, dim_z = vid.shape

    imgs = []
    try:
        for ax in axs.ravel():
            imgs.append(ax.imshow(videos[0][0, ...]))
    except:
        imgs.append(axs.imshow(videos[0][0, ...]))

    def update(frame):
        for n in range(nx * ny):
            imgs[n].set_array(videos[n][frame, ...])
        return imgs

    print(f'Generating FuncAnimation...')

    ani = FuncAnimation(fig, update, frames=nb_frames, blit=True, interval=300)
    plt.tight_layout()
    writergif = PillowWriter(fps=nb_frames)
    ani.save(filename=str(final_filename) + ".gif", writer=writergif)#, fps=nb_frames)

    plt.show()




def set_labels(x: Param, y: Param, axs):
    for k in ["x", "y"]:
        for i, v in enumerate(locals()[k].values):
            try :
                ax = (axs if k == "x" else axs.T)[0, i]
            except :
                try :
                    ax = (axs if k == "x" else axs.T)[i]
                except :
                    ax=axs
            try:
                getattr(ax, f"set_{k}ticks")([sum(getattr(ax, f"get_{k}lim")()) / 2])
                getattr(ax, f"set_{k}ticklabels")([f"{v}"])
            except TypeError:
                pass



def prepare_canvas(x: Param, y: Param, title=None, **kw):
    plt.rcParams["xtick.bottom"] = plt.rcParams["xtick.labelbottom"] = False
    plt.rcParams["xtick.top"] = plt.rcParams["xtick.labeltop"] = True
    plt.rcParams["ytick.left"] = plt.rcParams["ytick.labelleft"] = True
    pltnot = dict(top=False, bottom=False, left=False, right=False)

    nx, ny = len(x.values), len(y.values)
    fig, axs = plt.subplots(nrows=ny, ncols=nx, sharex="col", sharey="row", **kw)

    try :
        for ii in axs.ravel():
            ii.tick_params(**pltnot)
    except:
        pass

    ax = fig.add_subplot(111, frameon=False)
    ax.tick_params(**pltnot, labelcolor="none")
    ax.xaxis.set_label_position("top")
    ax.set_xlabel(x.name, fontsize=14)
    ax.set_ylabel(y.name, fontsize=14)

    if title is not None:
        fig.suptitle(title)

    return fig, axs


def get_random(dims, frames):
    vid = [*dims, 3, frames]
    return np.random.rand(*vid)


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    _x = Param("lower_hertz", [0])#, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])#, 0.1, 0.2, 0.3])  # , 0.4, 0.5])
    _y = Param("upper_hertz", [1, 2, 3, 4, 5, 6])#, 1.2, 1.4, 1.6])  # , 0.9, 1])

    root = tf.Tree.new(__file__, "data")
    root.file(m="wrist.mp4")
    vid, fps = load_video_float(root.m)
    great_dico = {'amplification_factor': 100, 'lower_hertz': _x.values, 'upper_hertz': _y.values,
                  'pyramid_levels': 4}
    videos = apply_multiple_evms(vid, fps, great_dico)

    main(_x, _y, videos, "testtestvideo")

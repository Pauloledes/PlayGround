import gc
import logging
import shutil
from typing import NamedTuple, List
import matplotlib.pyplot as plt
import treefiles as tf
from eulerian_magnification.io import load_video_float
from matplotlib.animation import FuncAnimation, PillowWriter
from benchmark import apply_multiple_evms
import os
import numpy as np


class Param(NamedTuple):
    name: str
    values: List[float]


def main(x: Param, y: Param, videos_dir, final_filename):
    """
    Function allowing the creation of a dynamic plot containing x rows and y columns. Each row is a freq min while
    each column is a freq max. It is used to filter frequencies and amplify the moves
    from an initial video. Each video created has its frames stored in a folder. videos_dir is an array containing
    all the paths to the frames.
    A gif is finally created and contains the plot result.

    :param x: Array of the freq min to apply
    :param y: Array of the freq max to apply
    :param videos_dir: Array containing the paths to each folder containing all the frames
    :param final_filename: name of the gif created
    :return: None
    """

    fig, axs = prepare_canvas(x, y, figsize=(6, 6))
    nx, ny = len(x.values), len(y.values)
    set_labels(x, y, axs)

    nb_frames, dim_y, dim_x, dim_z = vid.shape

    imgs = []
    try:
        for ax in axs.ravel():
            imgs.append(ax.imshow(np.load(f'{videos_dir[0]}/F_0.npy')))
    except Exception as e:
        imgs.append(axs.imshow(np.load(f'{videos_dir[0]}/F_0.npy')))

    def update(frame):
        """
        Function used by FunAnimation to concatenate the frames in the final plot
        :param frame: number of the frame to add
        :return:
        """
        for n in range(nx * ny):
            imgs[n].set_array(np.load(f'{videos_dir[n]}/F_{frame}.npy'))
        return imgs

    print(f'Generating FuncAnimation...')
    ani = FuncAnimation(fig, update, frames=nb_frames, blit=True, interval=300, repeat=False)
    plt.tight_layout()
    writergif = PillowWriter(fps=nb_frames)
    ani.save(filename=f'{final_filename}.gif', writer=writergif)  
    plt.show()


def set_labels(x: Param, y: Param, axs):
    """
    Function allowing to label the plot where the videos will be stored in.
    :param x: Array of the freq min to apply
    :param y: Array of the freq max to apply
    :param axs: axs to work on
    :return: None
    """
    for k in ["x", "y"]:
        for i, v in enumerate(locals()[k].values):
            try:
                ax = (axs if k == "x" else axs.T)[0, i]
            except:
                try:
                    ax = (axs if k == "x" else axs.T)[i]
                except:
                    ax = axs
            try:
                getattr(ax, f"set_{k}ticks")([sum(getattr(ax, f"get_{k}lim")()) / 2])
                getattr(ax, f"set_{k}ticklabels")([f"{v}"])
            except TypeError:
                pass


def prepare_canvas(x: Param, y: Param, title=None, **kw):
    """
    Function allowing the build of a plot where the videos will be stored in.
    :param x: Array of the freq min to apply
    :param y: Array of the freq max to apply
    :param title: optional, title of the plot
    :param kw: other keywords
    :return: fig, axs
    """

    plt.rcParams["xtick.bottom"] = plt.rcParams["xtick.labelbottom"] = False
    plt.rcParams["xtick.top"] = plt.rcParams["xtick.labeltop"] = True
    plt.rcParams["ytick.left"] = plt.rcParams["ytick.labelleft"] = True
    pltnot = dict(top=False, bottom=False, left=False, right=False)

    nx, ny = len(x.values), len(y.values)
    fig, axs = plt.subplots(nrows=ny, ncols=nx, sharex="col", sharey="row", **kw)

    try:
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


def save_frames(videos):
    """
    Save of the frames of each videos magnified via EVM in a folder named upon the characteristics of the
    transformation performed
    :param videos: Array of string containing the names of all the videos created by EVM
    :return: videos_dir : Array of string containing the paths to each folder containing the frames for each video.
    Each frame is stored in the npy extension
    """

    videos_dir = []

    for v in videos:
        video_to_work_with, _ = load_video_float(v)
        string_v = v[:-4]
        videos_dir.append(string_v)

        if not os.path.exists(string_v):
            os.mkdir(string_v)

        for i, frame in enumerate(video_to_work_with):
            frame = frame[..., ::-1]
            np.save(f'{string_v}/F_{i}', frame)

        del video_to_work_with
        gc.collect()
    return videos_dir


def delete_dirs(videos_dir):
    """
    Once all the actions have been performed, this function allows the delete of all the folders containing the frames
    :param videos_dir: Array of string containing the paths to each folder containing the frames for each video
    :return: None
    """
    for folder in videos_dir:
        shutil.rmtree(folder)


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    _x = Param("lower_hertz", [0, 0.2, 0.3, 0.4])#, 0.5])#, 0.6])#, 0.7, 0.8, 0.9])#, 0.1, 0.2, 0.3])  # , 0.4, 0.5])
    _y = Param("upper_hertz", [1, 2, 3, 4])#, 5, 6])#, 1.2, 1.4, 1.6])  # , 0.9, 1])

    root = tf.Tree.new(__file__, "data")
    root.file(m="wrist.mp4")
    vid, fps = load_video_float(root.m)
    great_dico = {'amplification_factor': 100, 'lower_hertz': _x.values, 'upper_hertz': _y.values,
                  'pyramid_levels': 4}
    videos = apply_multiple_evms(vid, fps, great_dico)
    videos_dir = save_frames(videos)

    main(_x, _y, videos_dir, "Final_gif")
    delete_dirs(videos_dir)

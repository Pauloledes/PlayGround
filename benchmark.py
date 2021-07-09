import logging
import treefiles as tf
from eulerian_magnification import eulerian_magnification
from eulerian_magnification.io import load_video_float, save_video
import gc
from cut_video import zoom, overlay_video


def apply_evm(vid, fps, videoname:str, area=None, dico=None):
    """
    Performs the eulerian video magnification for a given set of parameters on the given video
    :param vid: video to apply evm on
    :param fps: fps of the video
    :param videoname: name of the amplified video that will be saved
    :param dico: dictionary containing the set of parameters for evm
    :return: Magnified video
    """
    if dico is None:
        dico = {'amplification_factor': 100, 'lower_hertz': 0, 'upper_hertz': 1, 'pyramid_levels': 4}

    lower_hertz = dico['lower_hertz']
    upper_hertz = dico['upper_hertz']
    amplification_factor = dico['amplification_factor']
    pyramid_levels = dico['pyramid_levels']
    vid_to_return = eulerian_magnification(
        vid,
        fps,
        freq_min=lower_hertz,
        freq_max=upper_hertz,
        amplification=amplification_factor,
        pyramid_levels=pyramid_levels,
    )

    ####
    if area is not None:
        truncated_vid = zoom(vid_to_return, area)
        vid_to_return = overlay_video(truncated_vid, vid, fps, area, save=True, title=f'{videoname}')
    else:
        save_video(vid_to_return, fps, videoname)

    return vid_to_return


def run_loop(great_dico, dico, vid, video_name, fps, videos, area=None):
    """
    Function that calls apply_evm for all the parameters given
    :param great_dico: dictionary containing all the parameters
    :param dico: dicionary containing the set of parameters to apply evm with
    :param vid: video to apply evm on
    :param video_name : name fo the video to save
    :param fps: fps of the video
    :param videos: empty array where the names of the magnified videos will be stored in
    :return: None
    """

    for j in range(len(great_dico['upper_hertz'])):
        dico['upper_hertz'] = great_dico['upper_hertz'][j]

        for k in range(len(great_dico['amplification_factor'])):
            dico['amplification_factor'] = great_dico['amplification_factor'][k]

            for l in range(len(great_dico['pyramid_levels'])):
                dico['pyramid_levels'] = great_dico['pyramid_levels'][l]
                name = f"{video_name[:-4]}_freqmin={str(dico['lower_hertz'])}_freqmax={str(dico['upper_hertz'])}" \
                        f"_ampli={str(dico['amplification_factor'])}.avi"

                if area is not None:
                    name = f'truncated_{name}'

                new_video_name = f'data/{name}'
                apply_evm(vid, fps, new_video_name, area, dico=dico)
                videos.append(new_video_name)
                gc.collect()


def apply_multiple_evms(vid, video_name, fps, great_dico, area):
    """
    Function that calls run_loop and return the results obtained
    :param vid: video to apply evm on
    :param fps: fps of the video
    :param great_dico: dictionary containing all the parameters
    :return:  array of string containing the names of the magnified videos
    """
    print(f'Applying EVM for set of parameters : {great_dico}')
    videos = []

    for i in range(len(great_dico['lower_hertz'])):
        dico = {}
        dico['lower_hertz'] = great_dico['lower_hertz'][i]
        run_loop(great_dico, dico, vid, video_name, fps, videos, area)
    del dico
    gc.collect()

    return videos


if __name__ == "__main__":
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    root = tf.Tree.new(__file__, "data")
    root.file(m="wrist.mp4")

    vid, fps = load_video_float(root.m)
    apply_evm(vid, fps, 'test')

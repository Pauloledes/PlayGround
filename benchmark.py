import logging
import treefiles as tf
from eulerian_magnification import eulerian_magnification
from eulerian_magnification.io import load_video_float, save_video
import gc


def apply_evm(vid, fps, videoname:str, dico=None):
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
    save_video(vid_to_return, fps, videoname)
    return vid_to_return


def run_loop(great_dico, dico, vid, fps, videos):
    """
    Function that calls apply_evm for all the parameters given
    :param great_dico: dictionary containing all the parameters
    :param dico: dicionary containing the set of parameters to apply evm with
    :param vid: video to apply evm on
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

        #
        # try:
        #     for k in range(len(great_dico['amplification_factor'])):
        #         dico['amplification_factor'] = great_dico['amplification_factor'][k]
        # except TypeError:
        #     dico['amplification_factor'] = great_dico['amplification_factor']
        #
        # try:
        #     for l in range(len(great_dico['pyramid_levels'])):
        #         dico['pyramid_levels'] = great_dico['pyramid_levels'][l]
        # except TypeError:
        #     dico['pyramid_levels'] = great_dico['pyramid_levels']

                name = f"EVM_freqmin={str(dico['lower_hertz'])}_freqmax={str(dico['upper_hertz'])}" \
                       f"_ampli={str(dico['amplification_factor'])}.avi"
                print(f'name={name}')
                video_name = f'data/{name}'
                print(f'video_name{video_name}')
                print(f'dico{dico}')
                apply_evm(vid, fps, video_name, dico=dico)
                videos.append(video_name)
                gc.collect()


def apply_multiple_evms(vid, fps, great_dico):
    """
    Function that calls run_loop and return the results obtained
    :param vid: video to apply evm on
    :param fps: fps of the video
    :param great_dico: dictionary containing all the parameters
    :return:  array of string containing the names of the magnified videos
    """
    print(f'Applying EVM for set of parameters : {great_dico}')
    videos = []
    # try:
    #     for i in range(len(great_dico['lower_hertz'])):
    #         dico = {}
    #         dico['lower_hertz'] = great_dico['lower_hertz'][i]
    # except TypeError:
    #     dico = {'lower_hertz': great_dico['lower_hertz']}
    # run_loop(great_dico, dico, vid, fps, videos)
    # del dico
    # gc.collect()

    for i in range(len(great_dico['lower_hertz'])):
        dico = {}
        dico['lower_hertz'] = great_dico['lower_hertz'][i]
        run_loop(great_dico, dico, vid, fps, videos)
    del dico
    gc.collect()

    return videos


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    params = dict(
        freq_min=[0, 0.2, 0.4],
        freq_max=[1, 1.2, 1.4],
    )
    root = tf.Tree.new(__file__, "data")
    root.file(m="wrist.mp4")
    vid, fps = load_video_float(root.m)
    apply_evm(vid, fps, 'test')

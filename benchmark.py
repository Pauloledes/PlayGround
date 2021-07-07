import logging
import treefiles as tf
from eulerian_magnification import eulerian_magnification
from eulerian_magnification.io import load_video_float, save_video
import gc
import numpy as np


def apply_evm(vid, fps, videoname:str, dico=None):
    if dico is None:
        dico = {'amplification_factor': 100, 'lower_hertz': 0, 'upper_hertz': 1, 'pyramid_levels': 4}

    lower_hertz = dico['lower_hertz']
    upper_hertz = dico['upper_hertz']
    amplification_factor = dico['amplification_factor']
    pyramid_levels = dico['pyramid_levels']
    vid = eulerian_magnification(
        vid,
        fps,
        freq_min=lower_hertz,
        freq_max=upper_hertz,
        amplification=amplification_factor,
        pyramid_levels=pyramid_levels,
    )
    save_video(vid, fps, videoname)
    return vid


def run_loop(great_dico, dico, vid, fps, videos):
    for j in range(len(great_dico['upper_hertz'])):
        dico['upper_hertz'] = great_dico['upper_hertz'][j]

        try:
            for k in range(len(great_dico['amplification_factor'])):
                dico['amplification_factor'] = great_dico['amplification_factor'][k]
        except TypeError:
            dico['amplification_factor'] = great_dico['amplification_factor']

        try:
            for l in range(len(great_dico['pyramid_levels'])):
                dico['pyramid_levels'] = great_dico['pyramid_levels'][l]
        except TypeError:
            dico['pyramid_levels'] = great_dico['pyramid_levels']

        name = f"EVM_freqmin={str(dico['lower_hertz'])}_freqmax={str(dico['upper_hertz'])}" \
               f"_ampli={str(dico['amplification_factor'])}.avi"
        print(name)
        video_name = f'data/{name}'
        apply_evm(vid, fps, video_name, dico=dico)
        videos.append(video_name)
        gc.collect()

def apply_multiple_evms(vid, fps, great_dico):
    print(f'Applying EVM for set of parameters : {great_dico}')
    videos = []
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

import numpy as np
from eulerian_magnification.io import load_video_float, save_video
import treefiles as tf


def zoom(video, area:dict=None):
    """
    Take a video and return the same video zoomed upon the specified area
    :param video:
    :param area: dictionary containing infos for zoom, should be like this
     area = {'first_row': first_row, 'last_row': last_row, 'first_col' : first_col, 'last_col' : last_col}
    :return: - truncated_vid = array containing the truncated video obtained
             - area = reminder of the area selected, might be useful if needed by other functions
    """
    if area == None:
        first_row = 150
        last_row = 250

        first_col = 300
        last_col = 450

        area = {'first_row': first_row, 'last_row': last_row, 'first_col': first_col, 'last_col': last_col}


    truncated_vid = video[:, area['first_row']:area['last_row'], area['first_col']:area['last_col'], :]
    return truncated_vid


def overlay_video(vid1, vid2, fps, area, save:bool = True, title='overlaid_wrist'):
    """
    Overlay vid1 on an area from vid2. Obviously, vid1.shape shall be smaller than vid2.shape
    :param vid1: Video to overlay with
    :param vid2: Video overlaid
    :param area: Area where vid1 will be inserted in
    :param save: Boolean, if True the video created is saved
    :param title: if save=True, video name
    :return: overlaid_vid = array containing the overlaid video obtained
    """
    overlaid_vid = np.copy(vid2)

    for i1, i2 in zip(range(area['first_row'], area['last_row']), range(vid1.shape[1])):
        for j1, j2 in zip(range(area['first_col'], area['last_col']), range(vid1.shape[2])):
            overlaid_vid[:, i1, j1, :] = vid1[:, i2, j2, :]

    if save:
        if title.endswith('avi'):
            save_video(overlaid_vid, fps, f'{title}')
        else:
            save_video(overlaid_vid, fps, f'{title}.avi')

    return overlaid_vid


if __name__ == '__main__':
    #troncated video of the magnified first_video
    vid_now = 'troncated_wrist_amplified.avi'

    #initial video
    first_video = 'wrist.mp4'

    #magnified initial video
    vid_magnified = 'EVM_freqmin=0.4_freqmax=3_ampli=50.avi'

    root = tf.Tree.new(__file__, "data")
    root.file(m=vid_now)
    vid1, fps1 = load_video_float(root.m)
    print(vid1.shape)

    root = tf.Tree.new(__file__, "data")
    root.file(m=first_video)
    vid2, fps2 = load_video_float(root.m)
    print(vid2.shape)

    root = tf.Tree.new(__file__, "data")
    root.file(m=vid_magnified)
    vid3, fps3 = load_video_float(root.m)
    print(vid3.shape)

    first_row = 150
    last_row = 250

    first_col = 300
    last_col = 450

    area = {'first_row': first_row, 'last_row': last_row, 'first_col' : first_col, 'last_col' : last_col}
    area=None

    if area is not None:
        truncated_video = zoom(vid2, area)
        new_vid = f'test'

    # new_vid = f'overlaid_{first_video}_{vid_magnified[4:-4]}'
    overlay_video(truncated_video, vid2, area, save=True, title=new_vid)





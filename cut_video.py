from eulerian_magnification.io import load_video_float, save_video
import treefiles as tf



def zoom(video, area):
    truncated_vid = video[:, area['first_row']:area['last_row'], area['first_col']:area['last_col'], :]
    return truncated_vid


def overlay_video(vid1, vid2, area, save:bool = True, title='overlaid_wrist'):
    for i1, i2 in zip(range(area['first_row'], area['last_row']), range(vid1.shape[1])):
        for j1, j2 in zip(range(area['first_col'], area['last_col']), range(vid1.shape[2])):
            vid2[:, i1, j1, :] = vid1[:, i2, j2, :]

    if save:
        save_video(vid2, fps2, f'{title}.avi')

    return vid2



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

    truncated_video = zoom(vid3, area)

    new_vid = f'overlaid_{first_video}_{vid_magnified[4:-4]}'
    overlay_video(truncated_video, vid2, area, save=True, title=new_vid)





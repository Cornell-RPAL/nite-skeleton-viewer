#!/bin/python
'''Visualize NiTE skeleton objects as videos or images.'''

import logging
import pickle

import better_exceptions
import fire

import coloredlogs
import skeletons
import visualization

coloredlogs.install(level='INFO', fmt='%(name)s @ [%(asctime)s] %(levelname)s:\t%(message)s')

# pylint: disable=C0103
log = logging.getLogger('visualizer')


def run(recording_filename, make_image=False, path_prefix='', out_filename=None, start_time=None, end_time=None, show=False):
  '''The main point of entry for the viewer
  Args:
    recording_filename (string): The path to the skeleton recording file to use for the
    visualization.

    make_image (bool, optional): Make an animation if False, output a single frame if True. Defaults
    to False.

    path_prefix (string, optional): Save the generated visualization with the given prefix. Defaults
    to "".

    out_filename (string, optional): The filename to use for the output file. Defaults to the name
    of the recording filename with the appropriate extension tacked on.

    start_time (int, optional): A number of seconds into the recording at which to start the visualization.
    Defaults to None (meaning start at the beginning).

    end_time (int, optional): A number of seconds into the recording at which to stop the visualization.
    Defaults to None (meaning stop at the end of the recording).

    show (bool, optional): Whether or not to preview the visualization before saving. Defaults to
    False.

  Returns:
    Nothing
  '''
  log.info(f'Starting visualization with {recording_filename}')
  log.info(f'Reading skeleton frames from {recording_filename}...')
  skeleton_frames = []
  with open(recording_filename, 'rb') as skeleton_file:
    while True:
      try:
        skeleton_frames.append(pickle.load(skeleton_file))
      except EOFError:
        break

  if not skeleton_frames:
    log.error(f'{recording_filename} contained no skeleton frames!')
    return

  log.info(f'Loaded {len(skeleton_frames)} frames')
  log.info('Filtering calibration frames')
  skel_start = skeleton_frames[0][1]
  skeleton_frames = skeletons.filter_calibrating(skeleton_frames)
  log.info(f'{len(skeleton_frames)} frames of tracking data')
  log.info('Transforming timestamps to time offsets')
  skeleton_frames = skeletons.timestamps_to_deltas(skeleton_frames, skel_start)
  start_time = start_time if start_time else skeleton_frames[0][1] / 1e6
  end_time = end_time if end_time else skeleton_frames[-1][1] / 1e6
  # TODO: Verify more rigorously that the timestamps can be interpreted as microseconds
  log.info(f'Creating {"image" if make_image else "video"}')
  log.info(f'Starting at {start_time}s, ending at {end_time}s')
  start_time *= 1e6
  end_time *= 1e6
  skeleton_frames = [(s, t) for (s, t) in skeleton_frames if t >= start_time and t <= end_time]
  out_filename = out_filename if out_filename else recording_filename
  if make_image:
    visualization.make_image(skeleton_frames, f'{path_prefix}{out_filename}.png', show)
  else:
    visualization.make_video(skeleton_frames, f'{path_prefix}{out_filename}.mp4', show)


if __name__ == '__main__':
  fire.Fire(run)

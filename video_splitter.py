# Multiprocess frame extractor
#
# Responsible for taking a video and using as many processes as specified to
# extract possible WB frames.
from os import path, makedirs
from multiprocessing import Process

from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, CAP_PROP_FPS
from tqdm import tqdm

from video_extractor import VideoExtractor
from shared_counter import SharedCounter

class VideoWorker:
  def __init__(self, warp_bar_config, filename, directory, worker_id, frame_offset, frame_count, frames_processed):
    self.process = Process(target=VideoWorker.worker, \
      args=(warp_bar_config, filename, directory, worker_id, frame_offset, \
        frame_count, frames_processed,))
    self.process.start()
  
  def join(self):
    self.process.join()
  
  def terminate(self):
    self.process.terminate()
  
  @staticmethod
  def worker(warp_bar_config, filename, directory, worker_id, frame_offset, frame_count, frames_processed):
    try:
      stream = VideoCapture(filename)
      stream.set(CAP_PROP_POS_FRAMES, frame_offset)
      extractor = VideoExtractor(warp_bar_config, directory, stream, worker_id, frame_offset, frame_count, frames_processed)
      stream.release()
    except KeyboardInterrupt:
      pass

class VideoSplitter:
  def __init__(self, filename, directory):
    self.directory = directory
    self.filename = filename
    self.frames_processed = SharedCounter(0)

    # Ensure the working directory for extracted frames is created
    if not path.exists(self.directory):
      makedirs(self.directory)

    # Open the stream to query the frame count and frame rate
    stream = VideoCapture(self.filename)
    self.frames = int(stream.get(CAP_PROP_FRAME_COUNT))
    self.frames_per_second = stream.get(CAP_PROP_FPS)
    stream.release()

  def start(self, processes, warp_bar_config):
    frame_offset = 0
    frame_count = int(self.frames / processes)
    frame_remainder = int(self.frames % processes)

    # Create multiple worker processes for each frame window in the video
    self.workers = []
    for i in range(processes - 1):
      self.workers.append(VideoWorker(warp_bar_config, self.filename, \
        self.directory, i, frame_offset, frame_count, self.frames_processed))
      frame_offset += frame_count

    # The last worker may need to do more work if there's any remainder frames
    frame_count += frame_remainder
    self.workers.append(VideoWorker(warp_bar_config, self.filename, \
      self.directory, processes - 1, frame_offset, frame_count, self.frames_processed))

  def join(self):
    progress_bar = tqdm(total=self.frames, desc='Extracting frames'.ljust(60), \
      bar_format='{l_bar}{bar}|[{elapsed}<{remaining}]')
    try:
      last_frames_processed = self.frames_processed.value()
      while last_frames_processed < self.frames:
        current_frames_processed = self.frames_processed.value()
        delta_frames_processed = abs(current_frames_processed - last_frames_processed)
        progress_bar.update(delta_frames_processed)
        last_frames_processed = current_frames_processed
    except KeyboardInterrupt:
      raise
    finally:
      progress_bar.close()

    for worker in self.workers:
      worker.join()

  def terminate(self):
    for worker in self.workers:
      worker.terminate()
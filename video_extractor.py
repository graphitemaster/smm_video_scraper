from __future__ import annotations
from typing import List, Callable, Optional
from multiprocessing import Pool
from dataclasses import dataclass
from signal import signal, SIGINT, SIG_IGN

from numpy import ndarray, concatenate # type: ignore
import cv2 #type: ignore

@dataclass
class Rectangle:
  x: int
  y: int
  w: int
  h: int

@dataclass
class Strategy:
  name: str
  process: Callable[[ndarray], Optional[ndarray]]

@dataclass
class Result:
  strategy: Strategy
  frame_offset: int
  frame: ndarray

@dataclass
class VideoClip:
  filename: str
  frame_offset: int
  frame_count: int
  strategies: List[Strategy]

class VideoExtractor:
  __slots__ = ('_workers', '_clips')

  def __init__(self: VideoExtractor, filename: str, workers: int, strategies: List[Strategy]):
    self._workers = workers

    stream = cv2.VideoCapture(filename)
    frames = int(stream.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = stream.get(cv2.CAP_PROP_FPS)

    frame_offset = 0
    frame_count = int(frames / workers)

    self._clips = [] # type: List[VideoClip]
    for i in range(workers - 1):
      self._clips.append(VideoClip(filename, frame_offset, frame_count, strategies))
      frame_offset += frame_count

    frame_count += int(frames % workers)
    self._clips.append(VideoClip(filename, frame_offset, frame_count, strategies))

  def process(self: VideoExtractor) -> List[List[Result]]:
    pool = Pool(self._workers, initializer=self.worker_initializer)
    return pool.map_async(self.worker, self._clips).get()

  @staticmethod
  def worker(video_clip: VideoClip) -> List[Result]:
    frames: List[Result] = []

    stream = cv2.VideoCapture(video_clip.filename)
    stream.set(cv2.CAP_PROP_POS_FRAMES, video_clip.frame_offset)

    for i in range(video_clip.frame_count):
      grabbed, frame = stream.read()
      if not grabbed:
        break

      # Convert everything to grayscale to make it easier to work with
      image = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

      # Run the strategies and store results
      for strategy in video_clip.strategies:
        # https://github.com/python/mypy/issues/5485
        data = strategy.process(image.copy()) # type: ignore

        if data is not None:
          frames.append(Result(strategy, video_clip.frame_offset + i, data))

    stream.release()

    return frames
  
  @staticmethod
  def worker_initializer() -> None:
    signal(SIGINT, SIG_IGN)

# Extraction techniques
def transition(frame: ndarray) -> Optional[ndarray]:
  w = frame.shape[1]
  h = frame.shape[0]

  pixels = int(w*h)

  # The frame should be at least 70% black, otherwise it couldn't possibly be
  # a level transition screen
  zero = pixels - cv2.countNonZero(frame)
  if zero < pixels*0.70:
    return None

  # Search for the title box in the transition screen
  title = cv2.threshold(frame.copy(), 200, 255, cv2.THRESH_BINARY)[1]

  # Crop out the course box
  crop = Rectangle(int(0.150*w), int(0.075*h), int(0.700*w), int(0.130*h))
  title = title[crop.y:crop.y+crop.h, crop.x:crop.x+crop.w]

  # The result of the crop should be 80% non-black otherwise this is not
  # a course box
  if cv2.countNonZero(title) < crop.w*crop.h*0.80:
    return None

  # Crop out the area that contains the course code
  crop = Rectangle(int(0.412*w), int(0.340*h), int(0.200*w), int(0.035*h))
  frame = frame[crop.y:crop.y+crop.h, crop.x:crop.x+crop.w]

  # Only when there's at least 10% non-black in the result
  if cv2.countNonZero(frame) < crop.w*crop.h*0.10:
    return None

  return frame

def warpbar(frame: ndarray) -> Optional[ndarray]:
  w = frame.shape[1]
  h = frame.shape[0]

  pixels = int(w*h)

  # The frame should be at least 70% black, otherwise it couldn't possibly be
  # a level transition screen
  zero = pixels - cv2.countNonZero(frame)
  if zero < pixels*0.70:
    return None

  # Isolate bright areas
  frame = cv2.threshold(frame, 220, 255, cv2.THRESH_BINARY)[1]

  # Crop to area of interest
  crop = Rectangle(int(0.785*w), 0, int(0.214*w), int(0.032*h))
  frame = frame[crop.y:crop.y+crop.h, crop.x:crop.x+crop.w]

  # Only when there's at least 10% non-black in the result
  if cv2.countNonZero(frame) < crop.w*crop.h*0.10:
    return None

  return frame

WarpbarStrategy = Strategy('warpbar', warpbar)
TransitionStrategy = Strategy('transition', transition)
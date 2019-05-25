from __future__ import annotations
from typing import Optional

from pytube import YouTube, Stream # type: ignore

class VideoInfo:
  class ResolveFailure(Exception):
    pass

  __slots__ = ('url', 'id', 'title', 'stream', 'filesize')

  def __init__(self: VideoInfo, url: str, attempts: int = 5):
    self.url = url

    self.id = None
    self.title = None
    self.stream = None
    self.filesize = None

    # Try multiple times incase the network went down or YouTube is failing us
    for attempt in range(attempts):
      try:
        video = YouTube(url)
        self.id = video.video_id
        self.title = video.title
        self.stream = video.streams.filter(subtype='mp4', fps=30, res='720p').first()
        self.filesize = self._stream.filesize
        return
      except KeyError:
        pass

    raise VideoInfo.ResolveFailure(f'failed to resolve video {url}')
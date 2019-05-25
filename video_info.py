from __future__ import annotations
from typing import Optional

from pytube import YouTube, Stream # type: ignore

class VideoInfo:
  class ResolveFailure(Exception):
    pass

  __slots__ = ('_url', '_id', '_title', '_stream', '_filesize')

  def __init__(self: VideoInfo, url: str, attempts: int = 5):
    self._url = url

    self._id = None
    self._title = None
    self._stream = None
    self._filesize = None

    # Try multiple times incase the network went down or YouTube is failing us
    for attempt in range(attempts):
      try:
        video = YouTube(url)
        self._id = video.video_id
        self._title = video.title
        self._stream = video.streams.filter(subtype='mp4', fps=30, res='720p').first()
        self._filesize = self._stream.filesize
        return
      except KeyError:
        pass

    raise VideoInfo.ResolveFailure(f'failed to resolve video {url}')

  @property
  def id(self: VideoInfo) -> Optional[str]:
    return self._id

  @property
  def url(self: VideoInfo) -> str:
    return self._url
  
  @property
  def title(self: VideoInfo) -> Optional[str]:
    return self._title

  @property
  def stream(self: VideoInfo) -> Optional[Stream]:
    return self._stream

  @property
  def filesize(self: VideoInfo) -> Optional[int]:
    return self._filesize
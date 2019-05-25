from __future__ import annotations
from typing import Optional
from threading import Thread, Lock
from io import BytesIO

from video_info import VideoInfo

class VideoDownloader:
  class Data:
    __slots__ = ('_bytes')
    def __init__(self: VideoDownloader.Data, data: BytesIO = None):
      self._bytes = data

  __slots__ = ('_video', '_buffer', '_lock', '_progress', '_thread')

  def __init__(self: VideoDownloader, video: VideoInfo):
    self._video = video

    if self._video._stream:
      # Imbue the stream with on progress callback so we can monitor the download
      self._video._stream.on_progress = self.on_progress

    # Run the download off the main thread to not block ourselfs
    self._buffer = VideoDownloader.Data()
    self._lock = Lock()
    self._progress = 0
    self._thread = Thread(target=self.worker, args=(video.stream, self._buffer,))

  def start(self: VideoDownloader) -> None:
    self._thread.start()

  def join(self: VideoDownloader) -> None:
    self._thread.join()

  @property
  def buffer(self: VideoDownloader) -> Optional[BytesIO]:
    self.join()
    return self._buffer._bytes

  @property
  def progress(self: VideoDownloader) -> float:
    with self._lock:
      return self._progress

  @staticmethod
  def worker(stream, result: VideoDownloader.Data) -> None:
    result._bytes = stream.stream_to_buffer()
    if result._bytes:
      result._bytes.seek(0, 0)

  def on_progress(self, chunk, stream, bytes_remaining) -> None:
    progress = abs(bytes_remaining - self._video.filesize) / self._video.filesize
    with self._lock:
      self._progress = round(progress * 100.0, 2)
    stream.write(chunk)
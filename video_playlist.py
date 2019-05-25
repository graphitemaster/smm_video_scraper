from __future__ import annotations
from typing import List, Optional
from enum import Enum
from urllib.request import Request, urlopen

from pytube import Playlist # type: ignore

class VideoPlaylist:
  class SortBy(Enum):
    OLDEST = 0,
    NEWEST = 1

  __slots__ = ('_urls', '_filter')

  def __init__(self: VideoPlaylist, url: str, sort_by: VideoPlaylist.SortBy, custom_filter: Optional[str] = None):
    playlist = Playlist(url)
    playlist.populate_video_urls()

    self._urls: List[str] = playlist.video_urls

    if sort_by is VideoPlaylist.SortBy.NEWEST:
      self._urls.reverse()

    self._filter: Optional[str] = None
    if custom_filter:
      self._filter = f'"simpleText":"{custom_filter}"'

  def __iter__(self: VideoPlaylist) -> VideoPlaylist:
    return self
  
  def __next__(self: VideoPlaylist) -> str:
    if not len(self._urls):
      raise StopIteration
    
    if self._filter:
      while True:
        if not len(self._urls):
          raise StopIteration

        url = self._urls.pop()

        request = Request(url)
        request.add_header('Cache-Control', 'no-cache')
        request.add_header('Connection', 'keep-alive')
        request.add_header('Host', 'www.youtube.com')
        request.add_header('Pragma', 'no-cache')
        request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0')

        data = urlopen(request).read().decode('utf-8')

        if self._filter in data:
          return url
    else:
      return self._urls.pop()
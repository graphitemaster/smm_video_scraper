#!/usr/bin/env python3

from sys import argv
from os import path, listdir
from urllib.parse import urlparse

from pytube import extract

from video_downloader import VideoDownloader
from video_extractor import VideoExtractor, WarpbarStrategy, TransitionStrategy
from video_playlist import VideoPlaylist
from video_info import VideoInfo
from recognizer import Recognizer

def is_valid_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc, result.path])
  except:
    return False

if __name__ == '__main__':
  if len(argv) != 2:
    print(f'Usage {argv[0]} [yt-url|yt-playlist-url|file|directroy]')
    exit(0)

  if not is_valid_url(argv[1]):
    videos = []
    if path.isfile(argv[1]):
      videos.append(argv[1])
    elif path.isdir(argv[1]):
      for video in listdir(argv[1]):
        videos.append(f'{argv[1]}/{video}')

    for video in videos:
      print(f'Processing {video}')
      extractor = VideoExtractor(video, 8, [WarpbarStrategy, TransitionStrategy])
      flattened = [value for results in extractor.process() for value in results]
      recognizer = Recognizer(flattened, 8)
      results = recognizer.process()
      for result in results:
        if result:
          print(f'{result[0].frame_offset} via {result[0].strategy.name} is {result[1]}')
      # TODO remainder
  else:
    videos = []
    if '&list=' in argv[1]:
      playlist = VideoPlaylist(argv[1], 'Super Mario Maker')
      for video in playlist:
        try:
          videos.append(VideoInfo(argv[1]))
        except VideoInfo.ResolveFailure:
          print(f'Could not resolve {argv[1]}')
    else:
      try:
        videos.append(VideoInfo(argv[1]))
      except VideoInfo.ResolveFailure:
        print(f'Could not resolve {argv[1]}')
    
    for video in videos:
      print(f'Downloading {video.id} ...')
      downloader = VideoDownloader(video)
      downloader.start()
      downloader.join()

      # TODO store to a download directory


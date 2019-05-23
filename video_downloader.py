# Utility to download a video from YT
#
# NOTE: Always downloads 720p @ 30fps, video_extractor.py assumes 720p for the
# WB region and anything smaller makes Tesseract OCR less effective while anything
# larger results in diminishing returns in terms of performance.
#
# NOTE: The choice of 30fps makes the time stamps less accurate but it's half the
# work to process 30fps than it is 60fps. If you want more accurate captures you
# can change that here. The only valid values are 30 and 60.
FPS=30

from pytube import YouTube
from tqdm import tqdm

class VideoDownloader:
  def __init__(self, url, filename):
    self.video = YouTube(url, on_progress_callback=self.progress)
    self.stream = self.video.streams.filter(subtype='mp4', fps=FPS, res='720p').first()
    self.title = self.video.title
    self.filename = filename

    self.progress_bar = tqdm(total=self.stream.filesize, desc='Downloading {}'.format(self.title).ljust(60), bar_format='{l_bar}{bar}|[{elapsed}<{remaining}]')
  
  def start(self):
    self.stream.download(filename=self.filename)
    self.progress_bar.close()

  def progress(self, stream, chunk, file_handle, bytes_remaining):
    size = self.stream.filesize
    current = abs(bytes_remaining - size)
    self.progress_bar.update(abs(self.progress_bar.n - current))
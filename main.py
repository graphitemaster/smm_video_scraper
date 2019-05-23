#!/bin/python3
from sys import argv

from video_downloader import VideoDownloader
from video_splitter import VideoSplitter
from ocr import OCR
from config import Config

if __name__ == '__main__':
  splitter, ocr = None, None
  if len(argv) != 2:
    print('Usage {} [url]'.format(argv[0]))
  
  try:
    config = Config('config.json')

    downloader = VideoDownloader(argv[1], 'src')
    downloader.start()

    splitter = VideoSplitter('src.mp4', 'frames')
    splitter.start(config.split_processes, config.warp_bar)
    splitter.join()

    ocr = OCR('frames')
    ocr.start(config.ocr_processes)
    ocr.join()
  except KeyboardInterrupt:
    if splitter is not None:
      splitter.terminate()
    if ocr is not None:
      ocr.terminate()
    print('Terminated')
  except:
    print('Unknown error')

  if ocr is not None:
    print(ocr.results)
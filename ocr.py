#!/bin/python3

from os import environ, listdir

from PIL import Image
from multiprocessing import Pool
from pytesseract import image_to_string
from tqdm import tqdm

environ['TESSDATA_PREFIX'] = './'

class OCR:
  def __init__(self, directory):
    self.directory = directory
    self.frames = listdir(directory)
    self.results = []

  def start(self, processes):
    files = ['{}/{}'.format(self.directory, x) for x in self.frames]
    self.pool = Pool(processes)
    self.results = list(tqdm(self.pool.imap(self.process, files), \
      total=len(files), desc='Extracting text'.ljust(60), \
        bar_format='{l_bar}{bar}|[{elapsed}<{remaining}]'))

  def join(self):
    self.pool.close()
    self.pool.join()
  
  def terminate(self):
    self.pool.terminate()

  @staticmethod
  def process(frame):
    try:
      return (frame, ''.join([x for x in image_to_string(Image.open(frame), lang='warpbar').upper() if x in '0123456789ABCDEF']))
    except KeyboardInterrupt:
      pass
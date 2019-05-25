from __future__ import annotations
from typing import List, Optional, Tuple
from os import environ
from signal import signal, SIGINT, SIG_IGN
from multiprocessing import Pool

from PIL import Image # type: ignore
from pytesseract import image_to_string # type: ignore

from video_extractor import Result

environ['TESSDATA_PREFIX'] = './tess'

class Recognizer:
  __slots__ = ('_results', '_workers')

  def __init__(self, results: List[Result], workers: int):
    self._results = results
    self._workers = workers
  
  def process(self) -> List[Tuple[Result, Optional[str]]]:
    pool = Pool(self._workers, initializer=self._worker_initializer)
    return pool.map_async(self._worker, self._results).get()

  @staticmethod
  def _worker(result: Result) -> Optional[Tuple[Result, str]]:
    image = Image.fromarray(result.frame, mode='L')

    text: Optional[str] = None
    if result.strategy.name == 'warpbar':
      text = image_to_string(image, lang='warpbar')
    else:
      text = image_to_string(image, lang='eng')

    if text:
      # Convert everything to uppercase first
      text = text.upper()

      # 0-9A-F are the legal characters in a course code, however the OCR may have
      # made some trivial mistakes distinguishing some characters.
      #
      # Here we perform a very simple homoglyph substitution for things we can be
      # confident in.
      text = text.replace('I', '1')
      text = text.replace('O', '0')
      text = text.replace('Q', '0')
      text = text.replace('S', '5')
      text = text.replace('Z', '2')

      text = ''.join([x for x in text.upper() if x in '0123456789ABCDEF'])

      # When the length is sixteen characters and the seconds part is 0000 it's
      # likely a course code
      if len(text) == 16 and text[4:8] == '0000':
        return (result, text)

    return None

  # Ignore SIGINT inside worker processes so they don't get KeyboardInterrupt
  @staticmethod
  def _worker_initializer() -> None:
    signal(SIGINT, SIG_IGN)
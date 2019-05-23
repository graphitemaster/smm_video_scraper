# Extracts SMM WB frames from a CV VideoCapture stream.
#
# NOTE: The video_downloader.py code always downloads 720p videos because lower
# resolutions are problematic for Tesseract OCR and higher resolutions like 1080p
# are just diminishing returns in terms of performance. So these values are
# specifically for 720p videos.

from numpy import concatenate
from cv2 import cvtColor, copyMakeBorder, threshold, countNonZero, imwrite, \
  COLOR_RGB2GRAY, BORDER_CONSTANT, THRESH_BINARY

class VideoExtractor:
  def __init__(self, warp_bar_config, directory, stream, worker_id, frame_offset, frame_count, frames_processed):
    self.frames = 0

    for i in range(frame_count):
      grabbed, frame = stream.read()
      if not grabbed:
        break

      # Take the frame and crop it to where the WB is
      position = warp_bar_config.position
      size = warp_bar_config.size
      warpbar = self.crop(frame, position.x, position.y, size.w, size.h)

      # Take the crop and convert it to grayscale to make everything easier
      grayscale = cvtColor(warpbar, COLOR_RGB2GRAY)

      # Extract the individual parts of the WB
      #
      # This is done because the "in-between" parts often contain a lot of
      # background noise because the hyphen character used to delinate each set
      # of four characters is quite small. This improves OCR accuracy quite a
      # bit.
      #
      # We also avoid the second part of the WB too because it's always "0000",
      # reducing the amount of work needed by the OCR engine.
      section_size = warp_bar_config.section.size
      section_skip = warp_bar_config.section.skip
      a = self.crop(grayscale, (section_size.w + section_skip) * 0, 0, section_size.w, section_size.h)

      # Skipped because always "0000"
      '''
      b = self.crop(grayscale, (section_size.w + section_skip) * 1, 0, section_size.w, section_size.h)
      '''

      c = self.crop(grayscale, (section_size.w + section_skip) * 2, 0, section_size.w, section_size.h)
      d = self.crop(grayscale, (section_size.w + section_skip) * 3, 0, section_size.w, section_size.h)

      # Concatenate the parts together into one long strip along the X-axis
      result = concatenate((a, c, d), axis=1)

      # The OCR engine needs border pixels in order to find regions of text,
      # give it 10 pixels
      result = copyMakeBorder(result, top=10, bottom=10, left=10, right=10, borderType=BORDER_CONSTANT, value=[0])

      # Isolate white areas of the result (anything between 220-255 brightness)
      # making everything else solid black.
      result = threshold(result, 220, 255, THRESH_BINARY)[1]

      # Every pixel will be solid black unless the WB area had some values
      # between 220-255 brightness, as a heuristic we can assume that there
      # was text if at least 25% of the result has white pixels
      if countNonZero(result) > (section_size.w*section_size.h*3)*0.25:
        # Write the possible WB frame with the frame number as the name
        imwrite('{}/{}.png'.format(directory, frame_offset + i), result)
        self.frames += 1

      frames_processed.increment()

  @staticmethod
  def crop(img, x, y, w, h):
    return img[y:y+h, x:x+w]
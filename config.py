import json
from sys import exit

from vec2 import Vec2

class WarpbarSectionConfig:
  def __init__(self, size, skip):
    self.size = size
    self.skip = skip

class WarpbarConfig:
  def __init__(self, position, size, section_size, section_skip):
    self.position = position
    self.size = size
    self.section = WarpbarSectionConfig(section_size, section_skip)

class Config:
  def __init__(self, file_name):
    with open(file_name) as file_handle:
      try:
        data = json.load(file_handle)
        warp_bar = data['warp_bar']
        warp_bar_position = warp_bar['position']
        warp_bar_size = warp_bar['size']
        warp_bar_section = warp_bar['section']

        warp_bar_position = Vec2(int(warp_bar_position['x']), int(warp_bar_position['y']))
        warp_bar_size = Vec2(int(warp_bar_size['w']), int(warp_bar_size['h']))
        warp_bar_section_size = warp_bar_section['size']
        warp_bar_section_skip = int(warp_bar_section['skip'])
        warp_bar_section_size = Vec2(int(warp_bar_section_size['w']), int(warp_bar_section_size['h']))

        self.split_processes = int(data['split_processes'])
        self.ocr_processes = int(data['ocr_processes'])
        self.warp_bar = WarpbarConfig(warp_bar_position, warp_bar_size, \
          warp_bar_section_size, warp_bar_section_skip)

      except:
        print('Could not load configuration')
        raise
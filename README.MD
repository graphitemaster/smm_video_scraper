# SMM video scrapper
Given a YT URL of SMM game play can extract level codes and the timestamp in the URL of where that level was played as well as provide information about the level such as title and author.

This project was created to catalogue the levels that were played by the streamer [CarlSagan42](https://www.twitch.tv/carlsagan42) but it can work with any video from any streamer.

As an example, the following was automatically detected by this tool for [this video](https://youtu.be/sBUvj2eCdb8) with some additional code to search the SMM bookmark website for level info.
```
0580-0000-03E0-A554 00:09:21 "Uno Más: The Wiring Malfunction." by "Sus Door" 
3EB7-0000-03B9-A97D 00:23:02 "Uno Màs: NSMB turns into SMW" by "Robraf21"
26A8-0000-03E2-6319 00:32:18 "Charizard's Dungeon of Fire" by "crashbashr"
```

## Configuration
To use this tool you must first provide a `config.json` file containing a rough approximation of where in a **720p video** the level code region of the warp bar is, this is easily done by taking a frame of the video and finding the rectangle of the warp bar level code by hand. Here's an example configuration for CarlSagan42's videos in particular.

```json
{
  "split_processes": 4,
  "ocr_processes": 8,
  "warp_bar": {
    "position": { "x": 1006, "y": 4 },
    "size": { "w": 271, "h": 15 },
    "section": {
      "size": { "w": 56, "h": 15 },
      "skip": 14
    }
  }
}
```

**NOTE** This tool only downloads **720p** videos from YT at **30fps**; so your positions and sizes must be relative to that. The choice for this resolution and frame rate is simply because it offers the best balance of performance to accuracy.

The `split_processes` and `ocr_processes` values control how many threads of execution the video frame splitting code should use and the OCR processing code should use. As a rule of thumb, these values should not be bigger than the number of logical processors your system has.

### Training data
This tool takes advantage of [Tesseract OCR](https://en.wikipedia.org/wiki/Tesseract_(software)) to extract text from extracted frames. This requires training data of the specified font to be present otherwise the accuracy will be horrible, as such this depends on the choice of font used for the warp bar itself. The default is [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) and the appropriate training data for that is included as the file `warpbar.traineddata`. If the video uses a different font this training data will need to be independently generated. You can generate this training data with [Train Your Tesseract](http://trainyourtesseract.com/). Just be sure to disable everything but **Uppercase Letters** and **Numbers**. Then  replace the `warpbar.traineddata` file.

## Performance
The slowest process is extracting text from the frames, as a consequence the OCR and frame extraction processes have been decoupled to improved performance.

A one hour video takes approximately **~10 minutes** to process on my i7-4790K @ 4GHz

Depending on your configuration you may want to play with `split_processes` and `ocr_processes` to fully saturate your hardware.

_Actual performance may vary depending on system configuration, tasks and internet speed_

## Running
Specify the URL on the command line with `./main.py [url]` and wait.

## Dependencies
* python3
* tesseract
* opencv2 `cv2`
* python-pillow `PIL`
* python-tesseract `pytesseract`
* python-tqdm `tqdm`
* python-pytube `pytube`
* python-numpy `numpy`

Those dependencies can be installed with `pip`
```
$ pip install opencv-python pil pytesseract tqdm pytube numpy
```

You'll also need **~2GiB** of RAM, **~256 MiB** of hard drive space **per hour** of video processed to store extracted frames and at least **~1GiB** to store the downloaded video itself.
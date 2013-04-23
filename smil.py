#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Standard:
import glob
import itertools
import os
import os.path
import re
import shutil
import subprocess
import sys
import time


class UnsupportedVideoException (Exception):
    pass


def get_smil(video):
    (height, width) = get_video_size(video)
    
    return """
<?xml version="1.1"?>
<smil xmlns="http://www.w3.org/ns/SMIL" version="3.0">
  <head>
    <meta name="Date" content="{date}"/>
    <layout>
      <root-layout width="{width}" height="{height}"/>
      <region id="video" width="100%" height="100%"/>
    </layout>
  </head>
  <body>
    <video region="video" src="{filename}"/>
  </body>
</smil>
    """.strip().format(
        date = get_video_date(video),
        filename = video,
        height = height,
        width = width)


def get_video_date(path):
    ctime = os.path.getctime(path)
    mtime = os.path.getmtime(path)
    
    return time.strftime('%Y-%m-%d', time.gmtime(min(ctime, mtime)))


def get_video_size(path):
    try:
        subprocess.check_output(['ffmpeg', '-i', path],
            stderr = subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        size = re.findall(rb'Video:[^\n]+ (\d{2,})x(\d{2,})', error.output)
    
    if len(size) == 0:
        raise UnsupportedVideoException()
    else:
        return reversed(list(map(int, size[0])))


videos = sys.argv[1:]

if len(videos) == 0:
    sys.exit('Usage: <video> ...')

if shutil.which('ffmpeg') is None:
    sys.exit('FFmpeg not in path. Install it from <http://www.ffmpeg.org/>.')

if os.name == 'nt':
    videos = itertools.chain.from_iterable(map(glob.glob, videos))

for video in videos:
    try:
        smil = get_smil(video)
    except UnsupportedVideoException:
        print('Error:', video, file = sys.stderr)
        continue
    else:
        print('Ok:', video)
    
    with open(os.path.splitext(video)[0] + '.smil', 'w') as smil_file:
        smil_file.write(smil + '\n')
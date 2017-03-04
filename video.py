#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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

def exit_usage():
    sys.exit('Usage: audio|smil <video> ...')

def get_smil(tool, video):
    (height, width) = get_video_size(tool, video)
    
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

def get_video_size(tool, path):
    try:
        subprocess.check_output([tool, '-i', path],
            stderr = subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        size = re.findall(rb'Video:[^\n]+ (\d{2,})x(\d{2,})', error.output)

    if len(size) == 0:
        raise UnsupportedVideoException()
    else:
        return reversed(list(map(int, size[0])))

for candidate_tool in 'ffmpeg', 'avconv':
    if shutil.which(candidate_tool) is not None:
        tool = candidate_tool
        break
else:
    sys.exit('FFmpeg or avconv not in path: <http://www.ffmpeg.org>, <https://libav.org>.')

if len(sys.argv) <= 2:
    exit_usage()

(action, videos) = (sys.argv[1], sys.argv[2:])

if os.name == 'nt':
    videos = itertools.chain.from_iterable(map(glob.glob, videos))

if action == 'audio':
    for video in videos:
        audio = os.path.splitext(video)[0] + '.m4a'
        
        try:
            subprocess.check_output(
                args = [tool, '-i', video, '-vn', '-acodec', 'copy', audio],
                stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print('Error:', video, file = sys.stderr)
        else:
            print('Ok:', video)
elif action == 'smil':
    for video in videos:
        try:
            smil = get_smil(tool, video)
        except UnsupportedVideoException:
            print('Error:', video, file = sys.stderr)
        else:
            print('Ok:', video)
            
            with open(os.path.splitext(video)[0] + '.smil', 'w') as smil_file:
                smil_file.write(smil + '\n')
else:
    exit_usage()

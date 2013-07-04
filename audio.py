#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Standard:
import glob
import itertools
import os
import os.path
import shutil
import subprocess
import sys


videos = sys.argv[1:]

if len(videos) == 0:
    sys.exit('Usage: <video> ...')

if shutil.which('ffmpeg') is None:
    sys.exit('FFmpeg not in path. Install it from <http://www.ffmpeg.org/>.')

if os.name == 'nt':
    videos = itertools.chain.from_iterable(map(glob.glob, videos))

for video in videos:
    audio = os.path.splitext(video)[0] + '.m4a'
    
    try:
        subprocess.check_output(
            args = ['ffmpeg', '-i', video, '-vn', '-acodec', 'copy', audio],
            stderr = subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        print('Error:', video, file = sys.stderr)
    else:
        print('Ok:', video)

#!/usr/bin/env python

# http://opencv.willowgarage.com/wiki/Mac_OS_X_OpenCV_Port
# http://astrobeano.blogspot.com/2012/02/webcam-capture-with-python-on-mac-os-x.html

import sys
import time
import logging
import os.path
import tempfile
import re
import subprocess
import logging

import cv2

def capture(root):

    vidcap = cv2.VideoCapture()
    vidcap.open(0)

    retval, image = vidcap.retrieve()
    vidcap.release()
    
    now = int(time.time())
    fname = "%s.jpg" % now

    path = os.path.join(root, fname)

    cv2.imwrite(path, image)
    return path

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-T", "--timer", dest="timer", help="...", default=0)
    parser.add_option("-l", "--local", dest="local", help="", default=None)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    while True:

        try:
            logging.debug("taking a picture...")
            path = capture(opts.local)
        except Exception, e:
            log.error("unable to time a picture, because: %s" % e)
            time.sleep(0.5)
            continue

        # cat *.jpg | ffmpeg -f image2pipe -r 1/.5 -vcodec mjpeg -i - -vcodec libx264 out.mp4

        if not opts.timer:
            break

        logging.debug("sleep for %s seconds" % opts.timer)
        time.sleep(float(opts.timer))

    logging.info("all done")
    sys.exit()

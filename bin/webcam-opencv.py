#!/usr/bin/env python

# http://opencv.willowgarage.com/wiki/Mac_OS_X_OpenCV_Port
# http://astrobeano.blogspot.com/2012/02/webcam-capture-with-python-on-mac-os-x.html

import sys
import time
import logging
import os.path
import logging

import cv2

def capture(opts):

    vidcap = cv2.VideoCapture()
    vidcap.open(opts.camera)

    retval, image = vidcap.retrieve()
    vidcap.release()
    
    now = int(time.time())
    fname = "%s-camera-%s.jpg" % (now, opts.camera)

    path = os.path.join(opts.out, fname)

    cv2.imwrite(path, image)
    return path

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-T", "--timer", dest="timer", help="...", default=0, type='int')
    parser.add_option("-o", "--out", dest="out", help="", default=None)
    parser.add_option("-c", "--camera", dest="camera", help="", default=0, type='int')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    while True:

        try:
            logging.debug("taking a picture with camera %s" % opts.camera)
            path = capture(opts)
        except Exception, e:
            logging.error("unable to time a picture, because: %s" % e)
            time.sleep(0.5)
            continue

        # cat *.jpg | ffmpeg -f image2pipe -r 1/.5 -vcodec mjpeg -i - -vcodec libx264 out.mp4

        if not opts.timer:
            break

        logging.debug("sleep for %s seconds" % opts.timer)
        time.sleep(float(opts.timer))

    logging.info("all done")
    sys.exit()

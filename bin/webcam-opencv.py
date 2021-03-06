#!/usr/bin/env python

# http://opencv.willowgarage.com/wiki/Mac_OS_X_OpenCV_Port
# http://astrobeano.blogspot.com/2012/02/webcam-capture-with-python-on-mac-os-x.html

import sys
import time
import logging
import os.path
import logging
import ConfigParser

import cv2

def capture(camera, outdir):

    vidcap = cv2.VideoCapture()
    vidcap.open(camera)

    retval, image = vidcap.retrieve()
    vidcap.release()
    
    now = int(time.time())
    fname = "%s-camera-%s.jpg" % (now, camera)

    path = os.path.join(outdir, fname)
    print path

    cv2.imwrite(path, image)
    return path

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config', action='store', help='path to a loopr config file - see source code for a sample config')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    # MAYBE: allow CLI flags to override the config file?
    # parser.add_option("-T", "--timer", dest="timer", help="...", default=0, type='int')
    # parser.add_option("-o", "--out", dest="out", help="", default=None)
    # parser.add_option("-c", "--camera", dest="camera", help="", default=0, type='int')

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    camera = int(cfg.get('webcam-opencv', 'camera'))
    outdir = cfg.get('webcam-opencv', 'out')
    timeout = cfg.get('webcam-opencv', 'timeout')

    while True:

        try:
            logging.debug("taking a picture with camera %s" % camera)
            path = capture(camera, outdir)
        except Exception, e:
            logging.error("unable to time a picture, because: %s" % e)
            time.sleep(0.5)
            continue

        # cat *.jpg | ffmpeg -f image2pipe -r 1/.5 -vcodec mjpeg -i - -vcodec libx264 out.mp4

        if not timeout:
            break

        logging.debug("sleep for %s seconds" % timeout)
        time.sleep(float(timeout))

    logging.info("all done")
    sys.exit()

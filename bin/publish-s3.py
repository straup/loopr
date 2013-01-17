#!/usr/bin/env python

import time
import os.path
import logging
import subprocess
import redis

from watchdog.observers.fsevents import FSEventsObserver as Observer
from watchdog.events import FileSystemEventHandler

import multiprocessing

def publish(path, opts):

    root = os.path.dirname(path)
    fname = os.path.basename(path)

    # https://github.com/sbc/boto/blob/master/bin/s3put

    args = [
        "s3put",
        "-a", opts.accesskey,
        "-s", opts.secret,
        "-b", opts.bucket,
        "-g", "public-read",
        "-p", root,
        ]

    if opts.prefix:
        args.append("--key_prefix")
        args.append(opts.prefix)

    args.append(path)

    try:
        subprocess.check_call(args)
    except Exception, e:
        logging.error(e)
        return False

    os.unlink(path)

    aws_path = "%s/%s" % (opts.bucket, fname)
    url = 'http://s3.amazonaws.com/%s' % aws_path

    key = "loopr_%s" % opts.bucket.replace(".", "_")

    try:
        r = redis.Redis()
        r.publish(key, url)
    except Exception, e:
        print e

pool = multiprocessing.Pool()

#

class Eyeballs(FileSystemEventHandler):

    def __init__(self, observer, opts):
        self.observer = observer
        self.opts = opts

    def on_any_event(self, event):

        if event.event_type != 'created':
            return

        path = event.src_path

        # publish(path, opts)
        pool.apply_async(publish, (path, opts))
        

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-w", "--watch", dest="watch", help="", default=None)
    parser.add_option("-a", "--accesskey", dest="accesskey", help="", default=None)
    parser.add_option("-s", "--secret", dest="secret", help="", default=None)
    parser.add_option("-b", "--bucket", dest="bucket", help="", default=None)
    parser.add_option("-p", "--prefix", dest="prefix", help="", default=None)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    observer = Observer()
    event_handler = Eyeballs(observer, opts)

    observer.schedule(event_handler, path=opts.watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

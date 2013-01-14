#!/usr/bin/env python

import time
import os.path
import logging
import redis

from watchdog.observers.fsevents import FSEventsObserver as Observer
from watchdog.events import FileSystemEventHandler

import multiprocessing

# note awesome...

redis = redis.Redis()

def publish(path):
    
    # publish to s3 or other ?

    try:
        redis.publish('loopr', path)
    except Exception, e:
        pass

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

        pool.apply_async(publish, (path,))


if __name__ == '__main__':

    import sys
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-w", "--watch", dest="watch", help="", default=None)
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

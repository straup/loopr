#!/usr/bin/env python

import time
import os.path
import subprocess
import logging
import glob
import tempfile

from watchdog.observers.fsevents import FSEventsObserver as Observer
from watchdog.events import FileSystemEventHandler

import multiprocessing

def do_filtr(filtr_bin, path, outdir):

    # This will need to be fixed eventually
    # (20130114/straup)
    recipe = os.path.basename(filtr_bin)

    fname = os.path.basename(path)
    fname, ext = os.path.splitext(fname)
    ext = ext.replace(".", "")

    fname = "%s-%s.%s" % (fname, recipe, ext)

    tmpdir = tempfile.gettempdir()
    tmpfile = os.path.join(tmpdir, fname)

    subprocess.check_call([filtr_bin, path, tmpfile])

    if not os.path.exists(tmpfile):
        return False

    filtred_path = os.path.join(outdir, fname)
    os.rename(tmpfile, filtred_path)

    os.unlink(path)
    return True

pool = multiprocessing.Pool()

#

class Eyeballs(FileSystemEventHandler):

    def __init__(self, observer, opts):
        self.observer = observer
        self.opts = opts

        filtr = os.path.join(self.opts.filtr, 'recipes', self.opts.recipe)
        self.filtr_bin = os.path.realpath(filtr)

        for path in glob.glob("%s/*.jpg" % self.opts.watch):
            pool.apply_async(do_filtr, (self.filtr_bin, path, self.opts.out))
        
    def on_any_event(self, event):

        if event.event_type != 'created':
            return

        path = event.src_path

        # do_filtr(self.filtr_bin, path, self.opts.out)
        pool.apply_async(do_filtr, (self.filtr_bin, path, self.opts.out))

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-w", "--watch", dest="watch", help="", default=None)
    parser.add_option("-o", "--out", dest="out", help="", default=None)
    parser.add_option("-f", "--filtr", dest="filtr", help="The path to the filtr application", default=None)
    parser.add_option("-r", "--recipe", dest="recipe", help="The name of the filtr to apply", default='filtr')
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

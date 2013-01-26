#!/usr/bin/env python

import time
import os
import os.path
import subprocess
import logging
import glob
import tempfile
import ConfigParser

if os.uname() == 'Darwin':
    from watchdog.observers.fsevents import FSEventsObserver as Observer
else:
    from watchdog.observers import Observer

from watchdog.events import FileSystemEventHandler

import multiprocessing

def do_filtr(filtr_bin, path, outdir):

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

        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read(opts.config)

        self.watch = self.cfg.get('filtr', 'watch')
        self.out = self.cfg.get('filtr', 'out')

        filtr = os.path.join(self.cfg.get('filtr', 'filtr'), 'recipes', self.cfg.get('filtr', 'recipe'))
        filtr = os.path.realpath(filtr)

        self.filtr_bin = filtr

        leftovers = glob.glob("%s/*.jpg" % self.watch)

        for path in leftovers:
            pool.apply_async(do_filtr, (self.filtr_bin, path, self.out))
        
    def on_any_event(self, event):

        if event.event_type != 'created':
            return

        path = event.src_path

        pool.apply_async(do_filtr, (self.filtr_bin, path, self.out))

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config', action='store', help='path to a loopr config file - see source code for a sample config')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    # MAYBE: allow CLI flags to override the config file?
    # parser.add_option("-w", "--watch", dest="watch", help="", default=None)
    # parser.add_option("-o", "--out", dest="out", help="", default=None)
    # parser.add_option("-f", "--filtr", dest="filtr", help="The path to the filtr application", default=None)
    # parser.add_option("-r", "--recipe", dest="recipe", help="The name of the filtr to apply", default='filtr')

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    observer = Observer()
    event_handler = Eyeballs(observer, opts)

    observer.schedule(event_handler, path=event_handler.watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

#!/usr/bin/env python

import time
import os
import os.path
import subprocess
import logging
import tempfile
import PIL.Image as Image

if os.uname() == 'Darwin':
    from watchdog.observers.fsevents import FSEventsObserver as Observer
else:
    from watchdog.observers import Observer

from watchdog.events import FileSystemEventHandler

import multiprocessing

def loopify(gifsicle, queue, outdir, maxwidth=None):

    gif_queue = []

    tmpdir = tempfile.gettempdir()

    for path in queue:

        fname = os.path.basename(path)
        fname, ext = os.path.splitext(fname)

        gif = os.path.join(tmpdir, "%s.gif" % fname)

        im = Image.open(path)
        sz = im.size

        # TO DO: account for tall things...

        if maxwidth:

            w = int(maxwidth)

            wpercent = (w/float(sz[0]))
            h = int((float(sz[1]) * float(wpercent)))

            im = im.resize((w, h))

        im = im.convert('P', palette=Image.ADAPTIVE)
        im.save(gif)

        if not os.path.exists(gif):
            continue

        gif_queue.append(gif)
        os.unlink(path)

    if len(gif_queue) == 0:
        return False

    outname = "loopr-%s.gif" % int(time.time())
    outfile = os.path.join(outdir, outname)

    logging.debug("write new loop to %s" % outfile)

    args = [
        gifsicle,
        "-w",
        "--loopcount",
        "--careful",
        ]

    # passing /some/dir/*.gif makes subcommands
    # freak out and generally be sad

    # also, passing very long arguments makes
    # something fail - probably a args list is
    # too long error...

    args.extend(gif_queue)

    args.extend(["-o", outfile])

    logging.debug(args)

    try:
        subprocess.check_call(args)
    except Exception, e:
        logging.error(e)

    for path in gif_queue:
        os.unlink(path)

pool = multiprocessing.Pool()

#

class Eyeballs(FileSystemEventHandler):

    def __init__(self, observer, opts):
        self.observer = observer
        self.opts = opts

        self.count = int(opts.count)
        self.queue = []

    def on_any_event(self, event):

        if event.event_type != 'created':
            return

        self.queue.append(event.src_path)

        logging.debug("queue length: %s (trigger at %s)" % (len(self.queue), self.count))

        if len(self.queue) >= self.count:
            queue = self.queue[:self.count]
            self.queue = self.queue[self.count:]

            logging.debug("loopify now")
            pool.apply_async(loopify, (self.opts.gifsicle, queue, self.opts.out, self.opts.maxwidth))

if __name__ == '__main__':

    import sys
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-w", "--watch", dest="watch", help="", default=None)
    parser.add_option("-o", "--out", dest="out", help="", default=None)
    parser.add_option("-c", "--count", dest="count", help="", default=200)
    parser.add_option("--gifsicle", dest="gifsicle", help="", default="/usr/local/bin/gifsicle"),    
    parser.add_option("--max-width", dest="maxwidth", help="", default=None)
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

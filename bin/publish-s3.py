#!/usr/bin/env python

import time
import os
import os.path
import logging
import subprocess
import redis
import ConfigParser

if os.uname() == 'Darwin':
    from watchdog.observers.fsevents import FSEventsObserver as Observer
else:
    from watchdog.observers import Observer

from watchdog.events import FileSystemEventHandler

import multiprocessing

def publish(cfg, path):

    s3put = cfg.get('publish-s3', 's3put')

    aws_key = cfg.get('publish-s3', 'aws_key')
    aws_secret = cfg.get('publish-s3', 'aws_secret')
    s3_bucket = cfg.get('publish-s3', 's3_bucket')
    s3_prefix = cfg.get('publish-s3', 's3_prefix')

    root = os.path.dirname(path)
    fname = os.path.basename(path)

    # https://github.com/sbc/boto/blob/master/bin/s3put

    args = [
        s3put,
        "-a", aws_key,
        "-s", aws_secret,
        "-b", s3_bucket,
        "-g", "public-read",
        "-p", root,
        ]

    if s3_prefix != '':
        args.append("--key_prefix")
        args.append(s3_prefix)

    args.append(path)

    try:
        subprocess.check_call(args)
    except Exception, e:
        logging.error(e)
        return False

    os.unlink(path)

    aws_parts = [ s3_bucket ]

    if s3_prefix != '':
        aws_parts.append(s3_prefix)

    aws_parts.append(fname)

    aws_path = "/".join(aws_parts)
    url = 'http://s3.amazonaws.com/%s' % aws_path

    channel = cfg.get('publish-s3', 'pubsub_channel')

    if channel != '' and fname.endswith('.gif'):

        try:

            logging.debug("push %s to '%s' channel" % (url, channel))

            r = redis.Redis()
            r.publish(channel, url)
        except Exception, e:
            print e

pool = multiprocessing.Pool()

#

class Eyeballs(FileSystemEventHandler):

    def __init__(self, observer, opts):
        self.observer = observer
        self.opts = opts

        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read(opts.config)

        self.watch = self.cfg.get('publish-s3', 'watch')

        self.s3put = self.cfg.get('publish-s3', 's3put')

        if not os.path.exists(self.s3put):
            raise Exception, "Can't find s3put (%s)" % self.s3put

    def on_any_event(self, event):

        path = None

        if event.event_type == 'created':
            path = event.src_path

        # WTF linux?

        elif event.event_type == 'moved':
            path = event.dest_path
        else:
            return False

        pool.apply_async(publish, (self.cfg, path))
        

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config', action='store', help='path to a loopr config file - see source code for a sample config')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    # MAYBE: allow CLI flags to override the config file?
    # parser.add_option("-w", "--watch", dest="watch", help="", default=None)
    # parser.add_option("-a", "--accesskey", dest="accesskey", help="", default=None)
    # parser.add_option("-s", "--secret", dest="secret", help="", default=None)
    # parser.add_option("-b", "--bucket", dest="bucket", help="", default=None)
    # parser.add_option("-p", "--prefix", dest="prefix", help="", default=None)

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

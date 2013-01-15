#!/usr/bin/env python

import redis
import tempfile
import json
import os.path
import logging

def syndicate(urls, bucket, pending='/Users/asc/Desktop/loopr'):

    # print urls

    fname = "%s.bucket"

    try:
        tmpdir = tempfile.gettempdir()
        index = os.path.join(tmpdir, fname)

        fh = open(index, 'w')
        json.dump(urls, fh, indent=2)
        fh.close()
    
        pending_path = os.path.join(pending, fname)
        os.rename(index, pending_path)

    except Exception, e:
        print e

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-b", "--bucket", dest="bucket", help="", default=None)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    channel = "loopr_%s_gif" % opts.bucket

    r = redis.Redis()

    ps = r.pubsub()
    ps.subscribe(channel)

    while True:

        for item in ps.listen():

            if item['type'] != 'message':
                continue

            elif item['channel'] == channel:

                r.lpush('loopr_urls', data)
                r.ltrim('loopr_urls', 0, 100)
                urls = r.lrange('loopr_urls', 0, 15)

                syndicate(urls, opts.bucket)
                    
            else:
                pass

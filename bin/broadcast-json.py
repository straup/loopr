#!/usr/bin/env python

import redis
import tempfile
import json
import os.path
import logging
import ConfigParser

def syndicate(urls, outfile):

    try:

        fname = os.path.basename(outfile)

        tmpdir = tempfile.gettempdir()
        tmpfile = os.path.join(tmpdir, fname)

        fh = open(index, 'w')
        json.dump(urls, fh, indent=2)
        fh.close()
    
        os.rename(tmpfile, outfile)

    except Exception, e:
        print e

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config', action='store', help='path to a loopr config file - see source code for a sample config')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    # MAYBE: allow CLI flags to override the config file?
    # parser.add_option("-b", "--bucket", dest="bucket", help="", default=None)
    # parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)
    # parser.add_option("-c", "--count", dest="count", action="store", help="number of loops to include", default=15, type='int')

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    channel = cfg.get('broadcast-json', 'channel')
    count = cfg.get('broadcast-json', 'count')
    outfile = cfg.get('broadcast-json', 'outfile')
    
    r = redis.Redis()

    ps = r.pubsub()
    ps.subscribe(channel)

    while True:

        for item in ps.listen():

            if item['type'] != 'message':
                continue

            elif item['channel'] == channel:

                r.lpush('loopr_urls', item['data'])
                r.ltrim('loopr_urls', 0, 100)
                urls = r.lrange('loopr_urls', 0, count)

                syndicate(urls, outfile)
                    
            else:
                pass

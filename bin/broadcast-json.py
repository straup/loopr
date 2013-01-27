#!/usr/bin/env python

import redis
import tempfile
import json
import os.path
import logging
import ConfigParser

def syndicate(urls, outdir, channel):

    try:

        fname = "%s.json" % channel
        outfile = os.path.join(outdir, fname)

        tmpdir = tempfile.gettempdir()
        tmpfile = os.path.join(tmpdir, fname)

        data = { 'loops': urls }

        fh = open(tmpfile, 'w')
        json.dump(data, fh, indent=2)
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

    channel = cfg.get('broadcast-json', 'pubsub_channel')
    count = cfg.get('broadcast-json', 'count')
    outdir = cfg.get('broadcast-json', 'out')
    
    r = redis.Redis()

    ps = r.pubsub()
    ps.subscribe(channel)

    while True:

        for item in ps.listen():

            logging.debug(item)

            if item['type'] != 'message':
                continue

            elif item['channel'] == channel:

                r.lpush('loopr_urls', item['data'])
                r.ltrim('loopr_urls', 0, 100)
                urls = r.lrange('loopr_urls', 0, count)

                syndicate(urls, outdir, channel)
                    
            else:
                pass

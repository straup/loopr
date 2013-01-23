#!/usr/bin/env python

import redis
import tempfile
import json
import os.path
import logging
import feedformatter

def syndicate(urls, opts, pending='/Users/asc/Desktop/loopr'):

    feed = Feed()

    feed.feed["title"] = ""
    feed.feed["link"] = ""
    feed.feed["author"] = ""
    feed.feed["description"] = ""

    for u in urls:

        fq_url = ''

        desc = '<img src="%s" />' % fq_url

        item = {}
        item["title"] = os.path.basename(u)
        item["link"] = fq_url
        item["description"] = descr
        item["pubDate"] = time.localtime()
        item["guid"] = "1234567890"
    
        feed.items.append(item)

    rss1 = "%s_rss1.xml" % opts.bucket
    rss2 = "%s_rss2.xml" % opts.bucket
    atom = "%s_atom.xml" % opts.bucket

    for out in (rss1, rss2, atom):

        try:
            tmpdir = tempfile.gettempdir()
            index = os.path.join(tmpdir, fname)

            pending_path = os.path.join(pending, out)

            if out.endswith('rss1.xml'):
                feed.format_rss1_file(pending_path)

            elif out.endswith('rss2.xml'):
                feed.format_rss2_file(pending_path)

            else:
                feed.format_atom_file(pending_path)

            os.rename(index, pending_path)

    except Exception, e:
        print e

if __name__ == '__main__':

    print "THIS DOESN'T WORK YET"
    sys.exit()

    import sys
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-b", "--bucket", dest="bucket", help="", default=None)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)
    parser.add_option("-c", "--count", dest="count", action="store", help="number of loops to include", default=15, type='int')

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    channel = "loopr_%s" % opts.bucket.replace(".", "_")

    r = redis.Redis()

    ps = r.pubsub()
    ps.subscribe(channel)

    while True:

        for item in ps.listen():

            print item

            if item['type'] != 'message':
                continue

            elif item['channel'] == channel:

                r.lpush('loopr_urls', item['data'])
                r.ltrim('loopr_urls', 0, 100)
                urls = r.lrange('loopr_urls', 0, opts['count'])

                syndicate(urls, opts)
                    
            else:
                pass

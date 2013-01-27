#!/usr/bin/env python

import redis
import tempfile
import json
import os.path
import logging
import feedformatter
import time

def syndicate(urls, opts):

    feed = feedformatter.Feed()

    feed.feed["title"] = opts.bucket
    feed.feed["link"] = ""
    feed.feed["author"] = "loopr"
    feed.feed["description"] = ""

    for url in urls:

        title = os.path.basename(url)
        desc = '<img src="%s" />' % url

        guid = "%s-%s" % (opts.bucket, title)

        item = {}
        item["title"] = title
        item["link"] = url
        item["description"] = descr
        item["pubDate"] = time.localtime()
        item["guid"] = guid
    
        feed.items.append(item)

    rss1 = "%s_rss1.xml" % opts.bucket
    rss2 = "%s_rss2.xml" % opts.bucket
    atom = "%s_atom.xml" % opts.bucket

    for what in (rss1, rss2, atom):

        try:
            tmpdir = tempfile.gettempdir()

            pending_path = os.path.join(tmpdir, what)
            publish_path = os.path.join(opts.opt, what)

            if out.endswith('rss1.xml'):
                feed.format_rss1_file(pending_path)

            elif out.endswith('rss2.xml'):
                feed.format_rss2_file(pending_path)

            else:
                feed.format_atom_file(pending_path)

            os.rename(pending_path, publish_path)

        except Exception, e:
            logging.error("failed to write %s: %s" % (what, e))

if __name__ == '__main__':

    import sys
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-b", "--bucket", dest="bucket", help="", default=None)
    parser.add_option("-o", "--out", dest="out", help="", default=None)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)
    parser.add_option("-c", "--count", dest="count", action="store", help="number of loops to include", default=15, type='int')

    (opts, args) = parser.parse_args()

    print "THIS DOESN'T WORK YET"
    sys.exit()

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

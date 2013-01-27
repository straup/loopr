#!/usr/bin/env python

import redis
import tempfile
import json
import os.path
import logging
import feedformatter
import time
import hashlib
import ConfigParser

def syndicate(urls, cfg):

    feed = feedformatter.Feed()

    feed.feed["title"] = cfg.get('broadcast-syndication-feeds', 'title')
    feed.feed["link"] = cfg.get('broadcast-syndication-feeds', 'link')
    feed.feed["author"] = cfg.get('broadcast-syndication-feeds', 'author')
    feed.feed["description"] = cfg.get('broadcast-syndication-feeds', 'description')

    for url in urls:

        title = os.path.basename(url)
        desc = '<img src="%s" />' % url

        hash = hashlib.md5()
        hash.update(url)

        guid = hash.digest()

        item = {}
        item["title"] = title
        item["link"] = url
        item["description"] = desc
        item["pubDate"] = time.localtime()
        item["guid"] = guid
    
        feed.items.append(item)

    rss1 = "rss1.xml"
    rss2 = "rss2.xml"
    atom = "atom.xml"

    outdir = cfg.get('broadcast-syndication-feeds', 'out')

    for what in (rss1, rss2, atom):

        try:
            tmpdir = tempfile.gettempdir()

            pending_path = os.path.join(tmpdir, what)
            publish_path = os.path.join(outdir, what)

            if what.endswith('rss1.xml'):
                feed.format_rss1_file(pending_path)

            elif what.endswith('rss2.xml'):
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

    parser.add_option('-c', '--config', dest='config', action='store', help='path to a loopr config file - see source code for a sample config')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable chatty logging; default is false", default=False)

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    channel = cfg.get('broadcast-syndication-feeds', 'pubsub_channel')

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
                urls = r.lrange('loopr_urls', 0, 15)

                syndicate(urls, cfg)
                    
            else:
                pass

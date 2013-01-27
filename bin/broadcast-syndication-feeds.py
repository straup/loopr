#!/usr/bin/env python

import redis
import tempfile
import json
import os.path
import logging
import feedformatter
import time
import uuid
import re
import ConfigParser
import datetime

def syndicate(urls, cfg):

    feed = feedformatter.Feed()

    feed.feed["title"] = cfg.get('broadcast-syndication-feeds', 'title')
    feed.feed["link"] = cfg.get('broadcast-syndication-feeds', 'link')
    feed.feed["author"] = cfg.get('broadcast-syndication-feeds', 'author')
    feed.feed["description"] = cfg.get('broadcast-syndication-feeds', 'description')

    fname_pattern = re.compile('loopr-(\d+)\.gif')

    for url in urls:

        fname = os.path.basename(url)
        match = fname_pattern.match(fname)

        if match:
            groups = match.groups()
            ts = int(groups[0])
            dt = datetime.datetime.fromtimestamp(ts)

            title = dt.strftime('%HH%M')
            pubdate = time.localtime(ts)
        else:
            title = fname
            pubdate = time.localtime()

        desc = '<img src="%s" />' % url

        # So yeah... this causes the RSS2 serializer
        # to LOSE ITS MIND. Because... Guido?
        # hash = hashlib.md5()
        # hash.update(url)
        # guid = hash.digest()

        # TO DO: flags to generate guids using artisanal
        # integers...

        guid = uuid.uuid4()
        guid = str(guid)

        item = {}
        item["title"] = title
        item["link"] = url
        item["description"] = desc
        item["pubDate"] = pubdate
        item["guid"] = guid
    
	# Why you no stick <content> ?
        # https://code.google.com/p/feedformatter/source/browse/trunk/feedformatter.py#207
        # item["content"] = { 'content': desc, 'type': 'html' }

        feed.items.append(item)

    rss1 = "rss1.xml"
    rss2 = "rss2.xml"

    # This is not yet being produced because the <content> blob
    # is not being set correctly. See above. (20130127/straup)
    atom = "atom.xml"

    outdir = cfg.get('broadcast-syndication-feeds', 'out')

    for what in (rss1, rss2):

        logging.debug("generate %s" % what)

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

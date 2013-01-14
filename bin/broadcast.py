#!/usr/bin/env python

import redis
import multiprocessing
import tempfile
import json

# not awesome...

r = redis.Redis()

def publish(who, data):
    print "send %s to %s" % (data, who)

    r.lpush('loopr_urls', data)
    r.ltrim('loopr_urls', 0, 100)
    urls = r.lrange('loopr_urls', 0, 15)
    
    tmpdir = tempfile.gettempdir()
    index = os.path.join(tmpdir, 'index.json')

    fh = open(index, 'w')
    json.dump(fh, urls, indent=2)
    fh.close()

    print urls

    # websockets
    # https://github.com/straup/fancy-idling/blob/master/display.py

    # pubsubhub?

    # plain vanilla POST

pool = multiprocessing.Pool()

if __name__ == '__main__':

    def reload_subscriptions():

        # r.hsetnx('loopr_subscriptions', 'http://example.com', int(time.time()))
        # r.publish('loopr_subscriptions', 'O HAI')

        return r.hkeys('loopr_subscriptions')

    subscribers = reload_subscriptions()

    ps = r.pubsub()
    ps.subscribe(['loopr', 'loopr_subscriptions'])

    while True:

        for item in ps.listen():

            if item['type'] != 'message':
                continue

            if item['channel'] == 'loopr_subscriptions':
                subscribers = reload_subscriptions()

            elif item['channel'] == 'loopr':
                for who in subscribers:
                    pool.apply_async(publish, (who, item['data']))
                    
            else:
                pass

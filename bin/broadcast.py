#!/usr/bin/env python

import redis
import multiprocessing

def publish(who, data):
    print "send %s to %s" % (data, who)

    # websockets
    # https://github.com/straup/fancy-idling/blob/master/display.py

    # pubsubhub?

    # plain vanilla POST

pool = multiprocessing.Pool()

if __name__ == '__main__':

    r = redis.Redis()

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

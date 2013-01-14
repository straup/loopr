#!/usr/bin/env python

import redis
import multiprocessing

def publish(who, data):
    print "send %s to %s" % (data, who)

pool = multiprocessing.Pool()

if __name__ == '__main__':

    r = redis.Redis()

    ps = r.pubsub()
    ps.subscribe(['loopr'])

    subscribers = [ 'http://example.com' ]

    while True:

        for item in ps.listen():

            if item['type'] != 'message':
                continue
                
            for who in subscribers:
                pool.apply_async(publish, (who, item['data']))

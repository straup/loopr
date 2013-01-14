#!/usr/bin/env python

import redis
import multiprocessing
import tempfile
import json
import os.path

def syndicate(data, pending='/Users/asc/Desktop'):

    r.lpush('loopr_urls', data)
    r.ltrim('loopr_urls', 0, 100)
    urls = r.lrange('loopr_urls', 0, 15)

    print urls

    try:
        tmpdir = tempfile.gettempdir()
        index = os.path.join(tmpdir, 'index.json')

        fh = open(index, 'w')
        json.dump(fh, {'urls': urls}, indent=2)
        fh.close()
    
        pending_path = os.path.join(pending, 'index.json')
        print pending_path

        os.rename(index, pending_path)
    except Exception, e:
        print e

pool = multiprocessing.Pool()

if __name__ == '__main__':

    r = redis.Redis()

    ps = r.pubsub()
    ps.subscribe(['loopr_gif'])

    while True:

        for item in ps.listen():

            if item['type'] != 'message':
                continue

            elif item['channel'] == 'loopr_gif':
                syndicate(item['data'])
                # pool.apply_async(syndicate, (item['data'],))
                    
            else:
                pass

loopr
==

**loopr is very much a work in progress**

loopr is a suite of tools for creating and broadcasting a webcam made of
animated gifs and filters. 

The suite currently consists of (5) separate applications that all act
individually and communicate with one another by writing files to disk (or
sometimes using a shared memory pool (like Redis).

This is not the only way to do things but it was the quickest and dumbest way I
could get things working over a weekend spent with friends and a few hours at
the airport waiting for a red-eye.

The five steps are:

### Broadcasting

This will probably be renamed as `syndicate-json.py` and `syndicate-rss.py` and
so on.

	$> syndicate.py -b aws_bucket
      
### Publishing

This will probably be updated to not require passing your AWS credentials on the
command line. There will also eventually be a `publish-websockets.py` and so on.

	$> publish-s3.py -w /path/to/loopr-ed -b aws_bucket -a aws_key -s aws_secret

### Enloopifying

This requires that you have things like [gifsicle]() installed.

	$> loopify.py -w /path/to/filtr-ed/ -o /path/to/loopr-ed -c 10 -v --max-width 500

### Filtering

This requires that have a bloodier-than-bleeding-edge version of [filtr]()
installed.

	$> filtr.py -w /path/to/webcam -o /path/to/filtr-ed -f /usr/bin/filtr/ -r pxl

### Picture taking

This requires that you have [opencv]() installed (and a webcam)

	$> webcam.py -o /path/to/webcam -T 0

loopr
==

**loopr is very much a work in progress**

loopr is a suite of tools for creating and broadcasting a webcam made of animated gifs and filters.

For example...

	$> syndicate.py -b aws_bucket
      
	$> publish-s3.py -w /path/to/loopr-ed -b aws_bucket -a aws_key -s aws_secret

	$> loopify.py -w /path/to/filtr-ed/ -o /path/to/loopr-ed -c 10 -v --max-width 500

	$> filtr.py -w /path/to/webcam -o /path/to/filtr-ed -f /usr/bin/filtr/ -r pxl

	$> webcam.py -o /path/to/webcam -T 0

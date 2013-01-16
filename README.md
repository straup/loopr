loopr
==

**loopr is very much a work in progress**

loopr is a suite of tools for creating and broadcasting a webcam made of
animated gifs and filters. 

[Here's an example.](http://straup.github.com/loopr/)

The suite currently consists of (5) separate applications that all act
individually and communicate with one another by writing files to disk (or
sometimes using a shared memory pool (like Redis).

This is not the only way to do things but it was the quickest and dumbest way I
could get things working over a weekend spent with friends and a few hours at
the airport waiting for a red-eye.

The five steps are:

### Broadcasting

This will probably be renamed as `syndicate-json.py` and other scripts like
`syndicate-rss.py` and `syndicate-websockets.py` and so on will be added.

	$> syndicate.py -b aws_bucket
      
### Publishing

This will probably be updated to not require passing your AWS credentials on the
command line.

Currently this uses Redis (so that means having things like [Redis](http://redis.io/) installed)
to update the broadcasting piece but those two pieces (publishing and
broadcasting) might be taught how to use Amazon's native [simple notification
service](https://aws.amazon.com/sns/).

	$> publish-s3.py -w /path/to/loopr-ed -b aws_bucket -a aws_key -s aws_secret

### Enloopifying

This requires that you have things like [gifsicle](http://www.lcdf.org/gifsicle/) installed.

	$> loopify.py -w /path/to/filtr-ed/ -o /path/to/loopr-ed -c 10 -v --max-width 500

### Filtering

This requires that have a bloodier-than-bleeding-edge version of [filtr](https://github.com/straup/filtr/tree/heathr)
installed.

	$> filtr.py -w /path/to/webcam -o /path/to/filtr-ed -f /usr/bin/filtr/ -r pxl

### Picture taking

This requires that you have [opencv](http://opencv.willowgarage.com/wiki/) installed (and a webcam)

	$> webcam.py -o /path/to/webcam -T 0

There's also a "viewing" piece which will depend on the type of broadcasting you're doing. Take a look at the [www directory](https://github.com/straup/loopr/tree/master/www) for some sample code on displaying animated gifs broadcast as a JSON file, that is updated periodically.

To do
--

Lots.

* Documenting what's there, now.

* Daemonizing all the tools and possibly adding a handy controller to... control
  all the other pieces.
 
* The fancy stuff.

See also
--

* [like a dog humping your leg (with
  photos)](http://www.aaronland.info/weblog/2011/05/07/fancy/#likeadog) – a blog
  post about a real-time photo thing-y

* [about pua.spum.org](http://pua.spum.org/about) – the about page for just such
  a thing


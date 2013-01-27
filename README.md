loopr
==

**loopr is very much a work in progress**

loopr is a suite of tools for creating and broadcasting a webcam made of
animated gifs and filters. 

[Here's an example.](http://straup.github.com/loopr/)

How does it work
--

The suite currently consists of (5) separate applications that all act
individually and communicate with one another by writing files to disk (or
sometimes using a shared memory pool like Redis).

This is not the only way to do things but it was the quickest and dumbest way I
could get things working over a weekend spent with friends and a few hours at
the airport waiting for a red-eye.

The five steps are:

_Note: the `loopr.cfg` mentioned in all these examples is discussed in detail, below._

### Broadcasting

Currently there are two "broadcasters".

One just uploads a plain vanilla JSON file (with the URLs of the last `n` animated GIFs) to S3:

	$> broadcast-json.py -c loopr.cfg

_If you are publishing JSON files to S3 you will need to manually configure [Cross-Origin Resource Sharing](http://docs.aws.amazon.com/AmazonS3/latest/dev/cors.html) (CORS) for your S3 bucket, by hand. If you don't and your "viewer" is not also an S3-backed website then you won't be able to read the index of animated gifs._

The second broadcaster generates and uploads various syndication feeds (RSS 1.0; RSS 2.0) to S3:

	$> broadcast-syndication-feeds.py -c loopr.cfg

_Support for Atom syndication feeds is present but currently disabled until I can figure out why the `feedformatter` Python library isn't including little HTML blobs with the actual animated GIFs in its final output._

Eventually other scripts like [`broadcast-websockets.py`](https://github.com/straup/fancy-idling/blob/master/display.py) will be added.
      
### Publishing

There is currently one "publisher" that watches a folder for new files and then puts them in an S3 bucket. It uses the `s3put` script for uploading files which is included with the Python [boto](https://github.com/sbc/boto) libraries, so you'll need to make sure those are installed. Files are added with `public-read` permissions.

The publishing and broadcasting pieces use Redis (so that means having things like [Redis](http://redis.io/) installed)
to update the broadcasting piece but those two pieces (publishing and
broadcasting) might also be taught how to use Amazon's native [simple notification
service](https://aws.amazon.com/sns/).

	$> publish-s3.py -c loopr.cfg

### Enloopifying

This requires that you have things like [gifsicle](http://www.lcdf.org/gifsicle/) installed.

	$> loopify.py -c loopr.cfg

### Filtering

This requires version 1.0 (or higher) of [filtr](https://github.com/straup/filtr/).

	$> filtr.py -c loopr.cfg

### Picture taking

By default, this requires that you have [OpenCV](http://opencv.willowgarage.com/wiki/) installed (and a webcam).

	$> webcam-opencv.py -c loopr.cfg

OpenCV is actually pretty easy to install but on some flavours of Linux it can
be kind of fussy (read: I haven't figured out all the chanting I need to do to
make it work on a Raspberry Pi). If you can install the
[fswebcam](https://github.com/fsphil/fswebcam) application there's also a simple
wrapper tool for using that instead:

	$> webcam-fswebcam.sh /directory-where/photos-are/written-to /dev/video0 1280x720

_See the way there there's no config file being passed to the shell script. Yeah, I haven't really figured that part out yet..._

### Viewing pictures

There's also a "viewing" piece which will depend on the type of broadcasting you're doing. Take a look at the [www directory](https://github.com/straup/loopr/tree/master/www) for some sample code that displays animated gifs broadcast as a JSON file, that is updated periodically. [Like this.](http://straup.github.com/loopr/)

The config file
--

This is still a bit of a moving target and, as a result, some of the naming conventions might be suitably dumb and wrong.

### Picture taking

#### [webcam-opencv]

	[webcam-opencv]
	out=/path/to/loopr/webcam
	camera=0
	timeout=5

* out

* camera

* timeout

### Filtering

#### [filtr]

	[filtr]
	watch=/path/to/loopr/webcam
	out=/path/to/loopr/filtr
	filtr=/path/to/filtr
	recipe=pxl

### Enloopifying

#### [loopify]

	[loopify]
	watch=/path/to/loopr/filtr
	out=/path/to/loopr/publish
	gifsicle=/usr/local/bin/gifsicle
	count=5
	max-width=500

### Publishing

#### [publish-s3]

	[publish-s3]
	s3put=/usr/local/bin/s3put
	watch=/path/to/loopr/publish
	aws_key=YOUR_AWS_ACCESSKEY
	aws_secret=YOUR_AWS_SECRET
	s3_bucket=loopr-bucket
	s3_prefix=
	pubsub_channel=loopr_bucket

### Broadcasting

#### [broadcast-json]

	[broadcast-json]
	pubsub_channel=loopr_bucket
	count=20
	out=/path/to/loopr/publish

#### [broadcast-syndication-feeds]

	[broadcast-syndication-feeds]
	pubsub_channel=loopr_bucket
	out=/path/to/publish
	title=loopr
	link=http://straup.github.com/loopr
	author=loopr
	description=loop all the things

To do
--

Lots.

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

* [Simulate long-exposure photography with OpenCV](http://www.eliteraspberries.com/blog/2013/01/simulate-long-exposure-photography-with-opencv.html)

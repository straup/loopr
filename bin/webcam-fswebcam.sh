#!/bin/sh

OUT=$1

DEVICE=/dev/video1
RESOLUTION=1280x720
FSWEBCAM=`which fswebcam`

while [ 1 ]
do
    NOW=`date +%s`
    ${FSWEBCAM} --quiet --no-banner -d ${DEVICE} -r ${RESOLUTION} ${OUT}/webcam-${NOW}.jpg
    sleep 5
done
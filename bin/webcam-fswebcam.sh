#!/bin/sh

OUT=$1
DEVICE=$2
RESOLUTION=$3
FSWEBCAM=`which fswebcam`
SLEEP=10

while [ 1 ]
do
    NOW=`date +%s`
    ${FSWEBCAM} --no-banner -d ${DEVICE} -r ${RESOLUTION} ${OUT}/webcam-${NOW}.jpg
    sleep ${SLEEP}
done
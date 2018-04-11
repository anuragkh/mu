#!/bin/bash

FN_NAME=xc-enc_zYNLyfO0
REGION="us-east-1"

public_ip=$(wget -qO - http://169.254.169.254/latest/meta-data/public-ipv4)
STATEHOST=${1:-"$public_ip"}
KFDIST=${2:-"16"}
NWORKERS=${3:-"16"}
NOFFSET=${4:-"0"}
YVAL=${5:-"30"}
HOST="$public_ip"

echo "IP=[$public_ip]"
echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
echo "AWS_ROLE=$AWS_ROLE"

if [ -z "$PORTNUM" ]; then
    PORTNUM=13579
fi
if [ -z "$STATEPORT" ]; then
    STATEPORT=9090
fi
if [ -z "$STATETHREADS" ]; then
    STATETHREADS=24
fi
if [ ! -z "$DEBUG" ]; then
    DEBUG="-D"
else
    DEBUG=""
fi
if [ ! -z "$NOUPLOAD" ]; then
    echo "WARNING: no upload"
    UPLOAD=""
else
    UPLOAD="-u"
fi
if [ -z "$SSIM_ONLY" ]; then
    SSIM_ONLY=""
else
    SSIM_ONLY=1
fi
if [ -z "$FRAMES" ]; then
    NUM_FRAMES=6
else
    NUM_FRAMES=$FRAMES
fi
FRAME_STR=$(printf "_%02d" $NUM_FRAMES)
if [ -z "$SEVEN_FRAMES" ]; then
    VID_SUFFIX=$FRAME_STR
    XCENC_EXEC="xcenc"
    DUMP_EXEC="dump_ssim"
    FRAME_SWITCH=""
else
    VID_SUFFIX=""
    XCENC_EXEC="xcenc7"
    DUMP_EXEC="dump_ssim7"
    FRAME_SWITCH="-f $NUM_FRAMES"
fi

mkdir -p logs
LOGFILESUFFIX=k${KFDIST}_n${NWORKERS}_o${NOFFSET}_y${YVAL}_$(date +%F-%H:%M:%S)
echo -en "\033]0; ${REGION} ${LOGFILESUFFIX//_/ }\a"
set -u

if [ -z "$SSIM_ONLY" ]; then
    ./${XCENC_EXEC}_server.py \
        ${DEBUG} \
        ${UPLOAD} \
        ${FRAME_SWITCH} \
        -n ${NWORKERS} \
        -o ${NOFFSET} \
        -X $((${NWORKERS} / 2)) \
        -Y ${YVAL} \
        -K ${KFDIST} \
        -v sintel-4k-y4m"${VID_SUFFIX}" \
        -b elasticmem-datasets \
        -r ${REGION} \
        -l ${FN_NAME} \
        -t ${PORTNUM} \
        -h ${HOST} \
        -T ${STATEPORT} \
        -R ${STATETHREADS} \
        -H ${STATEHOST} \
	-c /tmp/mu_example/ssl/ca_cert.pem \
	-s /tmp/mu_example/ssl/server_cert.pem \
	-k /tmp/mu_example/ssl/server_key.pem \
        -O logs/${XCENC_EXEC}_transitions_${LOGFILESUFFIX}.log
fi

#if [ $? = 0 ] && [ ! -z "${UPLOAD}" ]; then
#    ./${DUMP_EXEC}_server.py \
#        ${DEBUG} \
#        -n ${NWORKERS} \
#        -o ${NOFFSET} \
#        -X $((${NWORKERS} / 2)) \
#        -Y ${YVAL} \
#        -K ${KFDIST} \
#        -v sintel-4k-y4m${FRAME_STR} \
#        -b excamera-${REGION} \
#        -r ${REGION} \
#        -l ${FN_NAME} \
#        -t ${PORTNUM} \
#        -h ${REGION}.x.tita.nyc \
#        -O logs/${DUMP_EXEC}_transitions_${LOGFILESUFFIX}.log
#fi

#!/bin/bash

export FN_NAME="xc-enc_CnF9QOeX"
export REGION="us-east-1"
export PUBLIC_IP=`curl --silent http://169.254.169.254/latest/meta-data/public-ipv4`
echo "IP=[$PUBLIC_IP]"
echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
echo "AWS_ROLE=$AWS_ROLE"

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "Usage: $0 kf_dist n_workers n_offset y_val"
    exit 1
fi

DEBUG=1
KFDIST=$1
NWORKERS=$2
NOFFSET=$3
YVAL=$4
if [ -z "$PORTNUM" ]; then
    PORTNUM=13579
fi
if [ -z "$STATEPORT" ]; then
    STATEPORT=13337
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

if [ -z "$SSL_DIR" ]; then
    SSL_DIR="/tmp/mu_example/ssl"
fi
export CA_CERT="$SSL_DIR/ca_cert.pem"
export SRV_CERT="$SSL_DIR/server_cert.pem"
export SRV_KEY="$SSL_DIR/server_key.pem"

if [ ! -f "$CA_CERT" ] || [ ! -f "$SRV_CERT" ] || [ ! -f "$SRV_KEY" ]; then
    echo "One or more of required SSL files misssing"
    exit -1
else
    echo "SSL: ($CA_CERT, $SRV_CERT, $SRV_KEY)"
fi

mkdir -p logs
LOGFILESUFFIX=k${KFDIST}_n${NWORKERS}_o${NOFFSET}_y${YVAL}_$(date +%F-%H:%M:%S)
echo -en "\033]0; ${REGION} ${LOGFILESUFFIX//_/ }\a"
set -u

#sleep 10

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
        -T ${STATEPORT} \
        -R ${STATETHREADS} \
        -H ${PUBLIC_IP} \
        -O logs/${XCENC_EXEC}_transitions_${LOGFILESUFFIX}.log \
	-t ${PORTNUM} \
	-h ${PUBLIC_IP}
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
#        -b elasticmem-datasets \
#        -r ${REGION} \
#        -l ${FN_NAME} \
#        -O logs/${DUMP_EXEC}_transitions_${LOGFILESUFFIX}.log \
#        -t ${PORTNUM} \
#	-h ${PUBLIC_IP}
#fi

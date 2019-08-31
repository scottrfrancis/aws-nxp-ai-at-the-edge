#!/bin/bash

CAM=/dev/video4
LOC=/home/torizon/recordings

APPROX_RECORD_TIME_IN_SECONDS=60
TIME_BETWEEN_PASTAS_IN_SECONDS=15
FRAMES=$(( 25*$APPROX_RECORD_TIME_IN_SECONDS ))

RESOLUTION=("640x480")
# RESOLUTION=("320x240" "640x480" "720x480" "1280x720" "1920x1080")
CBSPEED=("100" "75" "50" "25") # percentage
LEDB=("100" "75" "50" "25" "0") # percentage
PASTA_TYPES=("farfalle" "penne" "elbow" "shell" "miscellaneus")

function exit_gracefully {
	echo "Exiting gracefully..."
	gstpid=$(ps -e -o pid,comm | grep gst-launch-1.0 | awk {'print $1'})
	[ ! -z "$gstpid" ] && kill $gstpid && break
	/home/torizon/led_off.sh
	/home/torizon/cb_off.sh
	exit
}
trap exit_gracefully SIGINT SIGTERM

mkdir -p $LOC

echo "ATTENTION!!! READ THIS MESSAGE CAREFULLY!"
echo "To run this full script, it takes approximately:"
ss=$(( (${APPROX_RECORD_TIME_IN_SECONDS}+${TIME_BETWEEN_PASTAS_IN_SECONDS})*${#RESOLUTION[@]}*${#CBSPEED[@]}*${#LEDB[@]}*${#PASTA_TYPES[@]} ))
mm=$(( ${ss}/60 ))
hh=$(( ${mm}/60 ))
echo "$ss seconds;    $mm minutes;    $hh hours"
echo -e "Consider editing the parameters in this script if this is too much time\n\n"

echo "Starting in 15 seconds..."
echo "Capturing $FRAMES frames per pasta"

for resl in ${RESOLUTION[@]}; do
	for light in ${LEDB[@]}; do 
		for speed in ${CBSPEED[@]}; do
			for pasta in ${PASTA_TYPES[@]}; do
				echo "Next pasta: ${pasta}    led: ${light}    speed: ${speed}    resolution: ${resl}"
				sleep $TIME_BETWEEN_PASTAS_IN_SECONDS
				/home/torizon/cb_on.sh $speed
				/home/torizon/led_on.sh $light

				w=$(echo $resl | cut -d "x" -f 1)
				h=$(echo $resl | cut -d "x" -f 2)

				gst-launch-1.0 -q v4l2src num-buffers=$FRAMES device=$CAM ! \
					"video/x-raw,format=NV12,width=${w},height=${h}" ! \
					queue ! \
					v4l2h264enc ! \
					h264parse ! \
					matroskamux ! \
					filesink location=${LOC}/${pasta}_${speed}_${light}_${w}_${h}.mkv

				/home/torizon/led_off.sh
			done
		done
	done
done

# Wait last 15 seconds before shutting everythign down, to clean conveyor belt
sleep $TIME_BETWEEN_PASTAS_IN_SECONDS
/home/torizon/cb_off.sh
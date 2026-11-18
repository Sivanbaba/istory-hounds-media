#!/bin/bash
# sheet.sh in.mp4 out.jpg  -> 5 frames of vertical output side by side
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"); t=$(mktemp -d)
i=0; for f in 0.15 0.35 0.55 0.75 0.92; do ffmpeg -nostdin -loglevel error -y -ss $(python3 -c "print($d*$f)") -i "$1" -frames:v 1 -vf scale=360:640 $t/$i.png; i=$((i+1)); done
ffmpeg -nostdin -loglevel error -y -i $t/0.png -i $t/1.png -i $t/2.png -i $t/3.png -i $t/4.png -filter_complex hstack=5 "$2"; rm -r $t

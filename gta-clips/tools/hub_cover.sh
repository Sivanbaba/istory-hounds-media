#!/bin/bash
# hub_cover.sh out_k.mp4 -> out_k_c.mp4 : prepends a 0.3s still (frame at 1.5s) so the platform cover is a good frame.
# Book Hub media with thumbnail_timestamp_ms 100.
i="$1"; o="${i%.mp4}_c.mp4"; c="${i%.mp4}_cov.png"
ffmpeg -nostdin -loglevel error -y -ss 1.5 -i "$i" -frames:v 1 "$c"
ffmpeg -nostdin -loglevel error -y -loop 1 -t 0.3 -i "$c" -i "$i" -f lavfi -t 0.3 -i anullsrc=r=48000:cl=stereo -filter_complex "[0:v]fps=60,format=yuv420p,setsar=1[c];[1:v]setsar=1[m];[1:a]aresample=48000[ma];[c][2:a][m][ma]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$o" && echo "$o"

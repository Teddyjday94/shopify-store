#!/bin/bash
# Builds three 7-second solo posts from the commercial footage. Usage: bash edit/solo.sh
set -e; cd "$(dirname "$0")/.."; T=$(mktemp -d)
V="-c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -r 24 -an"
FIT="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,eq=contrast=1.04:saturation=1.03"
clip(){ # in start srcdur outdur overlay ovIn out   (outdur/srcdur sets slow-motion)
  ffmpeg -v error -y -i "$1" -loop 1 -t "$4" -i "$5" -filter_complex "[0:v]trim=start=$2:duration=$3,setpts=(PTS-STARTPTS)*$4/$3,$FIT[b];[1:v]format=rgba,fade=in:st=$6:d=0.35:alpha=1[t];[b][t]overlay=0:0:shortest=1" $V -t "$4" "$7"; }
push(){ # real print close-up: img dur out
  local f=$(echo "$2*24"|bc|cut -d. -f1)
  ffmpeg -v error -y -loop 1 -i "$1" -filter_complex "[0:v]scale=-2:2400,crop=1080:1920:(in_w-1080)/2:0,zoompan=z='1+0.0016*on':x='iw/2-(iw/zoom/2)':y='ih*0.18-(ih/zoom*0.18)':d=$f:s=1080x1920:fps=24,setsar=1" $V -t "$2" "$3"; }
endc(){ ffmpeg -v error -y -loop 1 -i edit/endcard.png -filter_complex "[0:v]zoompan=z='1.03-0.0005*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=48:s=1080x1920:fps=24,fade=in:st=0:d=0.2,setsar=1" $V -t 1.5 "$1"; }
cat3(){ printf "file '%s'\n" "$2" "$3" "$4" > $T/l.txt; ffmpeg -v error -y -f concat -safe 0 -i $T/l.txt -c copy -movflags +faststart "$1"; }
endc $T/end.mp4
# Creed / Masterless: full turn (4 s) + real print (1.5 s) + end card
clip raw/v2-creed-turn.mp4 0 6 4 edit/ov-masterless.png 2.6 $T/c1.mp4
push refs/print-masterless.jpg 1.5 $T/c2.mp4
cat3 final/solo-creed-masterless.mp4 $T/c1.mp4 $T/c2.mp4 $T/end.mp4
# Jax + Nova / King & Queen: first 3 s slowed to 4 s + both real prints (0.75 s each) + end card
clip raw/v4-king-queen.mp4 0 3 4 edit/ov-crowns.png 0.2 $T/k1.mp4
push refs/print-long-live-the-king.jpg 0.75 $T/k2a.mp4; push refs/print-queen-forever.jpg 0.75 $T/k2b.mp4
printf "file '%s'\n" $T/k2a.mp4 $T/k2b.mp4 > $T/kk.txt; ffmpeg -v error -y -f concat -safe 0 -i $T/kk.txt -c copy $T/k2.mp4
cat3 final/solo-king-queen.mp4 $T/k1.mp4 $T/k2.mp4 $T/end.mp4
# Rio / Rise From Ruin: first 2.8 s slowed to 3.7 s + real print (1.8 s) + end card
clip raw/v5-rio.mp4 0 2.8 3.7 edit/ov-rise.png 0.2 $T/r1.mp4
push refs/print-rise-from-ruin.jpg 1.8 $T/r2.mp4
cat3 final/solo-rio-rise-from-ruin.mp4 $T/r1.mp4 $T/r2.mp4 $T/end.mp4
rm -rf $T

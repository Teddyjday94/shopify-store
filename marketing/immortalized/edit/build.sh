#!/bin/bash
# Assembles the Immortalized commercial from raw/ clips + edit/ overlays. Usage: bash edit/build.sh [music.mp3]
set -e; cd "$(dirname "$0")/.."; T=$(mktemp -d); MUSIC="$1"
V="-c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -r 24 -an"
FIT="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,eq=contrast=1.04:saturation=1.03"
ov(){ # $1 in-video $2 start $3 dur $4 speed $5 overlay(or none) $6 overlay-in-time $7 out
  local f="[0:v]trim=start=$2:duration=$(echo "$3*$4"|bc -l),setpts=(PTS-STARTPTS)/$4,$FIT[b]"
  if [ "$5" = none ]; then ffmpeg -v error -y -i "$1" -filter_complex "$f" -map "[b]" $V "$7"
  else ffmpeg -v error -y -i "$1" -loop 1 -t "$3" -i "$5" -filter_complex "$f;[1:v]format=rgba,fade=in:st=$6:d=0.35:alpha=1[t];[b][t]overlay=0:0:shortest=1" $V -t "$3" "$7"; fi; }
ov raw/v1-hook.mp4        0   2.4 1    edit/ov-hook.png       0.15 $T/s1.mp4
ov raw/v2-creed-turn.mp4  0   4.0 1.5  edit/ov-masterless.png 2.6  $T/s2.mp4
# s3: real print close-up (no AI): slow push-in on the actual Masterless artwork
ffmpeg -v error -y -loop 1 -i refs/print-masterless.jpg -filter_complex "[0:v]scale=1400:-1,crop=1080:1920:(in_w-1080)/2:0,zoompan=z='1+0.0016*on':x='iw/2-(iw/zoom/2)':y='ih*0.18-(ih/zoom*0.18)':d=36:s=1080x1920:fps=24,setsar=1" $V -t 1.5 $T/s3.mp4
ov raw/v4-king-queen.mp4  0   3.0 1    edit/ov-crowns.png     0.2  $T/s4.mp4
ov raw/v5-rio.mp4         0   2.6 1    edit/ov-rise.png       0.2  $T/s5.mp4
ffmpeg -v error -y -loop 1 -i edit/endcard.png -filter_complex "[0:v]zoompan=z='1.04-0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=72:s=1080x1920:fps=24,fade=in:st=0:d=0.25,setsar=1" $V -t 3 $T/s6.mp4
cat > $T/m.txt <<L
file 's1.mp4'
file 's2.mp4'
file 's3.mp4'
file 's4.mp4'
file 's5.mp4'
file 's6.mp4'
L
ffmpeg -v error -y -f concat -safe 0 -i $T/m.txt -c copy $T/master.mp4
# 6-second ad cut: hook (1.4s) + Creed turn (3.1s) + end card (1.5s)
ffmpeg -v error -y -i $T/s1.mp4 -t 1.4 $V $T/a1.mp4
ffmpeg -v error -y -ss 0.9 -i $T/s2.mp4 -t 3.1 $V $T/a2.mp4
ffmpeg -v error -y -ss 1.5 -i $T/s6.mp4 -t 1.5 $V $T/a3.mp4
printf "file 'a1.mp4'\nfile 'a2.mp4'\nfile 'a3.mp4'\n" > $T/a.txt
ffmpeg -v error -y -f concat -safe 0 -i $T/a.txt -c copy $T/ad6.mp4
for n in master ad6; do
  if [ -n "$MUSIC" ]; then D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $T/$n.mp4)
    ffmpeg -v error -y -i $T/$n.mp4 -i "$MUSIC" -filter_complex "[1:a]atrim=0:$D,afade=out:st=$(echo "$D-0.6"|bc -l):d=0.6[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart final/immortalized-$n.mp4
  else ffmpeg -v error -y -i $T/$n.mp4 -c copy -movflags +faststart final/immortalized-$n-silent.mp4; fi
done
rm -rf $T; ls -la final

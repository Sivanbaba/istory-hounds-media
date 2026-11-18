# GTA 6 Twitch clip maker (12 Nov 2026)
Twitch link -> vertical 9:16 clip. Cloud env allows Twitch hosts (added 12 Nov). pip install yt-dlp first.
1. chat_spikes.py VOD_ID START END [STEP] > spikes.json   (samples chat replay; high vs_median = hype; the moment is ~10-40s BEFORE the chat spike)
2. grab.py VOD_URL START END raw.mp4 [1080p60]            (downloads only those 10s segments)
3. transcribe.py raw.mp4 words.json                       (Gemini 3.8 flash on 10s chunks, streamer speech only)
4. write spec.json (segments to keep, facecam box [x,y,w,h] on 1920x1080, hook text) -> render.py spec.json
   Captions: Montserrat Black Italic, white + yellow current word, black stroke; swears starred in captions; -14 LUFS.
Find facecam box: ffmpeg a still + crop. Demo: previews/2026-11-12 GTA clip demo/.

## Best source (12 Nov): Twitch top clips of the week
`yt-dlp --flat-playlist -J "https://www.twitch.tv/<channel>/clips?filter=clips&range=7d"` lists the most-viewed clips (title, views, duration);
`yt-dlp -f b -o x.mp4 https://www.twitch.tv/<ch>/clip/<slug>` downloads 1080p in seconds. Far better moments than chat-spike hunting.
Then transcribe.py -> spec -> render.py (one at a time) -> PFM upload (POST /media/create-upload-url, PUT file, use media_url).
Check the end of the clip for black frames (trim segments). If the source has burnt-in subtitles use "words": "wnone.json" ([]).
Posting script example: scratchpad post_b2.py pattern; ids logged in /mnt/project-files/gta-clips/posted_b*.json

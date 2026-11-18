# GTA 6 clip pages: handover (written 18 Nov 2026)

This file is everything a new project needs to run Sivan's three GTA 6 clip pages. It assumes no memory of the old project.

## The job

Sivan runs 3 clip pages. Each page posts on TikTok, Instagram and YouTube Shorts through **Post for Me (PFM)**:

| Page | TikTok | Instagram | YouTube |
|---|---|---|---|
| Bolted Clips | spc_PWq5BzlWpV4NYcu8i7Qfe | spc_k9WvI9Ip8vkbTZnAIciaU | spc_mfIszziXNV9dlWdcAeVk |
| The Streamer Hub | spc_aiarv0av0BGB2D60aS5Fg | spc_bAxFKMHpfikh3wTvGkLy | spc_UFEzbpNPPB1nGDt5NOAy |
| Anger Facts | spc_4r6HNZBE2IFX8KDlIf | spc_V00jmGukgjHYn0hWhfR8B | spc_9Pzev6dosx6niTesgu3n7 |

**Goals:**
- Streamer Hub YouTube to 1,000 subscribers.
- Views on GTA 6 clips, to earn from paid clipping campaigns. Whop Content Rewards: https://contentrewards.com/c/discover. No campaign joined yet.

Clips are posted automatically, with no preview step for Sivan. Don't send post links unless Sivan asks.

## Rules (latest wins)

**GTA 6 only (from 18 Nov)**
- Every clip is a GTA 6 moment from a famous streamer, e.g. Kai Cenat, xQc, OhnePixel, Jynxzi, Agent00, Lacy, Jasontheween, CaseOh.
- No small or random streamers.

**Volume and spacing**
- 5 clips per page per day, with a different clip on each page. Sivan's PFM plan allows 2,500 posts a month, so never go over 5 per page per day.
- Slots, all UTC (= UK time in winter). TikTok posts at the slot, Instagram 15 minutes later, YouTube 30 minutes later.
  - Bolted: 08:00, 11:00, 14:00, 17:00, 20:00
  - Hub: 09:00, 12:00, 15:00, 18:00, 21:00
  - Anger: 10:00, 13:00, 16:00, 19:00, 22:00
- Hub TikTok was restricted until Thu 19 Nov 09:00 UK. From then on it posts normally.

**Reviewer check (Sivan, 18 Nov)**
- Every clip goes to a separate reviewer agent before it is booked.
- Give the reviewer the 5-frame output sheet (`tools/sheet.sh out.mp4 sheet.jpg`) and a 3-frame source sheet.
- It must confirm all of these:
  - The main action or character is visible and centred.
  - The facecam shows the whole face.
  - No speaker is cut off.
  - There are no double or chopped captions.
  - No chat overlay junk shows.
  - The clip isn't dull (menus, maps, loading screens).
  - There is no banned content.
- Fix everything it flags and send it back for review. Drop clips that keep failing.

**Layout**
- Gaming clips: the streamer's facecam goes on top (about 35% of the frame) and the gameplay sits underneath.
- The face box w/h should be about 1.5. A tall box breaks the render.
- Only use clips with a visible facecam.
- Facecam positions:
  - Kai Cenat: bottom-left.
  - xQc: top-left or left-middle.
  - Lacy: top-left.
  - Jasontheween: right-middle.
- IRL clips use `mode: "cam"`, a single 9:16 crop. If two people talk, follow the speaker with a time-varying crop pre-source:
  ```
  ffmpeg crop=608:1080:'if(lt(t,T),X1,X2)':0
  ```
  Overlay it centred on a black 1920x1080 frame, then set `cam_cx` to 960.

**Captions**
- Burned-in captions are the most common problem.
- If the source already has burned-in captions, use `"words": "wnone.json"` (containing `[]`).
- Otherwise run `transcribe.py`.
- To cover old captions in IRL clips, use an opaque `drawbox ... color=black@1`.
- Trailer-reaction clips often get their subtitles chopped, so prefer real gameplay.

**Post captions**
- Every caption carries all the searchable keywords: the streamer's full name, GTA 6 / GTA VI, what happens (Vice City, police chase, and so on), and the credit `twitch.tv/<login>`.
- Use at most 5 hashtags.
- Hub captions end with "Subscribe for daily streamer clips 🔔".

**Hub cover**
- Run `tools/hub_cover.sh out_k.mp4`, then book the `_c.mp4` with `thumbnail_timestamp_ms` 100. `book.py` sets the timestamp automatically.
- Hub used to need a big female streamer in every clip. While no big female streamers play GTA 6, Hub takes any big streamer. Sivan hasn't confirmed this.

**Hard bans**
- No sexual or suggestive content.
- No nudity. GTA 6 has a nude shower scene, a strip club and characters in underwear in a drug lab.
- No revealing outfits. A strip club clip got taken down.
- No slurs.
- No animal cruelty.
- **Never ExtraEmily**, including clips about her.
- No sensitive identity or political topics.

## Tools (this folder)

- `engine/` is the clip engine.
  - `render.py spec.json` produces a 1080x1920 clip with the hook title, word captions and -14 LUFS audio.
  - `transcribe.py src.mp4 words.json` uses Gemini and needs `GEMINI_API_KEY` in the environment.
  - See `engine/README.md` for details.
- Spec keys:
  - Split mode: `face:[x,y,w,h]` on a 1920x1080 source, plus `game_cx`.
  - Cam mode: `mode:"cam"`, plus `cam_cx`.
  - Common: `hook` (use `\N` for a line break), `hook_s` 2.6, `words`, `segments [[start,end]]`, `punch []`, `src`, `out`.
  - Pre-scale any source that isn't 1920x1080.
- `tools/find_clips.py [since_iso] [logins…]` lists today's GTA VI Twitch clips per streamer. It uses public Twitch GQL with one login per query.
- To download a clip:
  ```
  yt-dlp -q -f b -o k.mp4 https://www.twitch.tv/<login>/clip/<slug> </dev/null
  ```
  Use `</dev/null` and `ffmpeg -nostdin` inside loops.
- `tools/sheet.sh` builds the reviewer sheets.
- `tools/book.py plan.json` books on PFM, can replace a booked clip, and logs ids. The docstring has the plan format.
- Keep a `used_slugs.txt` so a clip is never posted twice.
- Work in a scratch folder, not the repo. Never commit videos or `posted_*.json`.

## Keys and secrets (never put these in the repo, which is public)

- `POSTFORME_API_KEY`: Sivan copies it from the Post for Me dashboard (app.postforme.dev, under API keys) and adds it as an environment variable in the new project's cloud environment settings.
- `GEMINI_API_KEY` (optional `_2`, `_3`): from Google AI Studio, set the same way.
- If an account shows "needs reconnecting" (e.g. after a password change), get a reconnect link and send it to Sivan:
  ```
  POST https://api.postforme.dev/v1/social-accounts/auth-url {"platform": "...", "external_id": "..."}
  ```
- The network allowlist must include the Twitch hosts (gql.twitch.tv, usher/clips CDN hosts) and api.postforme.dev. The easiest setup is unrestricted network.

## PFM API cheat sheet

Base URL is `https://api.postforme.dev/v1`, with header `Authorization: Bearer $POSTFORME_API_KEY`.

| Task | Call |
|---|---|
| Upload | `POST /media/create-upload-url`, then PUT the file to `upload_url`, then use `media_url` |
| Create a post | `POST /social-posts` |
| Update a post | `PUT /social-posts/{id}` (needs the full body) |
| Delete a post | `DELETE /social-posts/{id}` |
| List scheduled posts | `GET /social-posts?social_account_id=&status=scheduled&limit=` |
| Check results | `GET /social-post-results?post_id=` |

PFM gives no Instagram stats.

## Queue at handover (18 Nov, UTC)

| Page | Time | Clip |
|---|---|---|
| Bolted | 15:30 | xQc's first crime in GTA 6 |
| Anger | 16:00 | xQc's car chase |
| Hub | 17:15 | xQc's first police chase (IG/YT) |
| Bolted | 18:00 | Kai Cenat's first drive |
| Anger | 20:30 | Agent00 meets a real-life Lucia |
| Hub | 21:15 | Jasontheween's road rage (IG/YT) |

The old project is still running:
- a top-up at 15:30 to fill tonight's open slots;
- the daily build at 17:00, which books Thu 19 and schedules itself for each following day.

When this new project takes over, tell the old project's clipping thread so it stops its scheduled runs. That way only one project books clips.

# Adding media

The site is built and ready; it just has no pictures yet. Every image and video slot shows a dark "slate" placeholder with the project title until the real file exists at the exact path below.

**How it works:** put the file at the path, run `python3 tools/build.py`, and the placeholder is replaced. Nothing else to edit. To see the expected path printed on each placeholder, open any page with `?slots` at the end of the URL, e.g. `http://localhost:8000/work/to-nora/?slots`.

`python3 tools/check.py` always prints the live list of what's present and what's missing, so you don't have to keep this table up to date by hand.

## Rules of thumb

- **Loops** (`hero.mp4`, `showreel.mp4` and other short clips) play muted, so leave the audio out. Keep them 6–15 seconds, MP4 / H.264, **under 8 MB**. 1920×1080 is ideal; 1280×720 is fine and smaller.
- **Posters** (`poster.jpg`) are the frame shown before a video loads, and the thumbnail on the home page grid. Use a strong frame from the loop. 1600×900 JPG.
- **Stills**: 1600 px wide JPG, quality ~80, under 400 KB each.
- **Before/after pairs** must be **exactly the same size and framing**, or the slider won't line up.
- **Full films and spots** (with sound) are usually too big for the repo. Upload them to YouTube (unlisted is fine) or Vimeo and paste the link into that slot's `"url"` in `data/projects.json`. The site shows your poster (or the YouTube thumbnail) and only loads the player when someone clicks, so it doesn't slow the page. If you leave `"url"` empty and add the local `.mp4`, it plays from the repo instead (keep it under 50 MB; GitHub refuses files over 100 MB).
- **Aspect ratio**: frames are 16:9 unless the slot sets `"aspect"` (the portrait is 4:5, the analytics screenshot 16:10). Other ratios are cropped to fit.
- **Client work**: only add frames you're allowed to show publicly.
- **PUMA concept**: don't add frames where the PUMA logo is the focus; the page states it's unofficial.
- Want WebP or a different file name? Change the path in `data/projects.json` to match. The path in the JSON is the only source of truth.

## Checklist

| Done | File | Where it shows | Format |
|---|---|---|---|
| [ ] | `media/reel/showreel.mp4` | Home · Showreel | MP4 H.264, 1920×1080 (or 1280×720), 6–15 s, muted, **under 8 MB** |
| [ ] | `media/reel/poster.jpg` | Home · Showreel | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/reel/showreel-full.mp4` | Home (optional) · Full showreel | Full piece with sound: better as a YouTube/Vimeo `url`; else MP4 H.264 + AAC, under 50 MB |
| [ ] | `media/reel/poster.jpg` | Home (optional) · Full showreel | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/about/portrait.jpg` | About · Portrait | JPG 1200×1500 (4:5), under 300 KB |
| [ ] | `media/client/hero.mp4` | Client work, Saudi production teams · Hero loop | MP4 H.264, 1920×1080 (or 1280×720), 6–15 s, muted, **under 8 MB** |
| [ ] | `media/client/poster.jpg` | Client work, Saudi production teams · Hero loop | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/client/train-before.jpg` | Client work, Saudi production teams · Rail campaign | JPG 1600×900, **same size as its "after"** |
| [ ] | `media/client/train-after.jpg` | Client work, Saudi production teams · Rail campaign | JPG 1600×900, **same size as its "before"** |
| [ ] | `media/client/historical-before.jpg` | Client work, Saudi production teams · Historical scene | JPG 1600×900, **same size as its "after"** |
| [ ] | `media/client/historical-after.jpg` | Client work, Saudi production teams · Historical scene | JPG 1600×900, **same size as its "before"** |
| [ ] | `media/client/ceiling-before.jpg` | Client work, Saudi production teams · Ceiling gag | JPG 1600×900, **same size as its "after"** |
| [ ] | `media/client/ceiling-after.jpg` | Client work, Saudi production teams · Ceiling gag | JPG 1600×900, **same size as its "before"** |
| [ ] | `media/client/headscarf.mp4` | Client work, Saudi production teams · Frozen performer | MP4 H.264, 1920×1080 (or 1280×720), 6–15 s, muted, **under 8 MB** |
| [ ] | `media/client/headscarf-poster.jpg` | Client work, Saudi production teams · Frozen performer | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/client/transition.mp4` | Client work, Saudi production teams · Extended camera move | MP4 H.264, 1920×1080 (or 1280×720), 6–15 s, muted, **under 8 MB** |
| [ ] | `media/client/transition-poster.jpg` | Client work, Saudi production teams · Extended camera move | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/to-nora/hero.mp4` | To Nora · Hero loop | MP4 H.264, 1920×1080 (or 1280×720), 6–15 s, muted, **under 8 MB** |
| [ ] | `media/to-nora/poster.jpg` | To Nora · Hero loop | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/to-nora/film.mp4` | To Nora · Watch the film | Full piece with sound: better as a YouTube/Vimeo `url`; else MP4 H.264 + AAC, under 50 MB |
| [ ] | `media/to-nora/poster.jpg` | To Nora · Watch the film | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/to-nora/still-1.jpg` | To Nora · Still 1 | JPG 1600 px wide, under 400 KB |
| [ ] | `media/to-nora/still-2.jpg` | To Nora · Still 2 | JPG 1600 px wide, under 400 KB |
| [ ] | `media/to-nora/still-3.jpg` | To Nora · Still 3 | JPG 1600 px wide, under 400 KB |
| [ ] | `media/to-nora/still-4.jpg` | To Nora · Still 4 | JPG 1600 px wide, under 400 KB |
| [ ] | `media/bloom/hero.mp4` | BLOOM: Too Fresh · Hero loop | MP4 H.264, 1920×1080 (or 1280×720), 6–15 s, muted, **under 8 MB** |
| [ ] | `media/bloom/poster.jpg` | BLOOM: Too Fresh · Hero loop | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/bloom/spot.mp4` | BLOOM: Too Fresh · Watch the spot | Full piece with sound: better as a YouTube/Vimeo `url`; else MP4 H.264 + AAC, under 50 MB |
| [ ] | `media/bloom/poster.jpg` | BLOOM: Too Fresh · Watch the spot | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/bloom/still-1.jpg` | BLOOM: Too Fresh · Still 1 | JPG 1600 px wide, under 400 KB |
| [ ] | `media/bloom/still-2.jpg` | BLOOM: Too Fresh · Still 2 | JPG 1600 px wide, under 400 KB |
| [ ] | `media/novara/hero.mp4` | NOVARA · Hero loop | MP4 H.264, 1920×1080 (or 1280×720), 6–15 s, muted, **under 8 MB** |
| [ ] | `media/novara/poster.jpg` | NOVARA · Hero loop | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/novara/spot.mp4` | NOVARA · Watch the spot | Full piece with sound: better as a YouTube/Vimeo `url`; else MP4 H.264 + AAC, under 50 MB |
| [ ] | `media/novara/poster.jpg` | NOVARA · Watch the spot | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/novara/comfyui-graph.png` | NOVARA · ComfyUI graph | PNG or JPG screenshot, 1600 px wide, under 500 KB |
| [ ] | `media/novara/keyframes.jpg` | NOVARA · Keyframe sequence | JPG 1600 px wide, under 400 KB |
| [ ] | `media/novara/logo-before.jpg` | NOVARA · Logo repair | JPG 1600×900, **same size as its "after"** |
| [ ] | `media/novara/logo-after.jpg` | NOVARA · Logo repair | JPG 1600×900, **same size as its "before"** |
| [ ] | `media/detailfixer/before.jpg` | ComfyUI-DetailFixer · Logo fix | JPG 1600×900, **same size as its "after"** |
| [ ] | `media/detailfixer/after.jpg` | ComfyUI-DetailFixer · Logo fix | JPG 1600×900, **same size as its "before"** |
| [ ] | `media/detailfixer/node.png` | ComfyUI-DetailFixer · Node in ComfyUI | PNG or JPG screenshot, 1600 px wide, under 500 KB |
| [ ] | `media/shotplanner/hero.png` | ComfyUI-ShotPlanner · Shot list | PNG or JPG screenshot, 1600 px wide, under 500 KB |
| [ ] | `media/shotplanner/nodes.png` | ComfyUI-ShotPlanner · Nodes in ComfyUI | PNG or JPG screenshot, 1600 px wide, under 500 KB |
| [ ] | `media/youtube/analytics.png` | AI YouTube channel · Analytics screenshot | PNG screenshot of YouTube Studio, 1600×1000, crop out anything private |
| [ ] | `media/puma/hero.mp4` | PUMA AI spec concept (unofficial) · Hero loop | MP4 H.264, 1920×1080 (or 1280×720), 6–15 s, muted, **under 8 MB** |
| [ ] | `media/puma/poster.jpg` | PUMA AI spec concept (unofficial) · Hero loop | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/puma/spot.mp4` | PUMA AI spec concept (unofficial) · Watch the concept | Full piece with sound: better as a YouTube/Vimeo `url`; else MP4 H.264 + AAC, under 50 MB |
| [ ] | `media/puma/poster.jpg` | PUMA AI spec concept (unofficial) · Watch the concept | JPG 1600×900, under 250 KB (a frame from the loop) |
| [ ] | `media/puma/still-1.jpg` | PUMA AI spec concept (unofficial) · Still 1 | JPG 1600 px wide, under 400 KB |
| [ ] | `media/puma/still-2.jpg` | PUMA AI spec concept (unofficial) · Still 2 | JPG 1600 px wide, under 400 KB |

## Compressing with ffmpeg

Install ffmpeg (`brew install ffmpeg` on macOS, `winget install ffmpeg` on Windows). Then:

**A muted web loop under 8 MB** (12 seconds from 0:03, 1080p, no audio):

```bash
ffmpeg -ss 3 -t 12 -i master.mov -an -vf "scale=1920:-2,fps=30" -c:v libx264 -preset slow -crf 26 -profile:v high -pix_fmt yuv420p -movflags +faststart media/to-nora/hero.mp4
```

Still over 8 MB? Raise `-crf` to 28–30, or go to 720p with `scale=1280:-2`.

**A poster frame** (the frame at 2 seconds of the loop):

```bash
ffmpeg -ss 2 -i media/to-nora/hero.mp4 -frames:v 1 -vf "scale=1600:-2" -q:v 3 media/to-nora/poster.jpg
```

**A still, resized and compressed** (PNG export to 1600 px JPG):

```bash
ffmpeg -i export.png -vf "scale=1600:-2" -q:v 3 media/to-nora/still-1.jpg
```

**A full film with sound**, if you host it in the repo rather than on YouTube/Vimeo:

```bash
ffmpeg -i film-master.mov -vf "scale=1920:-2" -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart media/to-nora/film.mp4
```

**Check sizes**, then rebuild and check:

```bash
du -h media/*/*
```

```bash
python3 tools/build.py && python3 tools/check.py
```

`check.py` warns about loops over 8 MB, images over 600 KB, and files in `media/` that no slot uses (usually a typo in the file name).

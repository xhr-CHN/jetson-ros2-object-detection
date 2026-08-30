# Final Jetson demo replacement design

## Goal

Replace the two separate Jetson demonstration videos in the current repository
snapshot with the user-selected combined video `jetson_demo.mp4`. Keep the previous
videos recoverable locally, update every user-facing link, and synchronize the final
selection to GitHub without rewriting repository history.

## Verified input

The selected source is `E:\机器人集成小组项目\jetson_demo.mp4`.

| Property | Value |
|---|---|
| Size | 8,331,319 bytes |
| SHA256 | `8D004988EB5021C3C0BEACEDF09E17637402166DB50598898170D7E3178BA28C` |
| Duration | 29.76 seconds |
| Video | H.264 Main, `yuv420p`, 1306 x 992, approximately 16 FPS |
| Audio | AAC LC, 48 kHz, stereo, 192 kb/s |

The complete file decodes without errors. Visual checks at 8 and 20 seconds show
simultaneous pencil and tennis-ball detections, bounding boxes, confidence values,
and approximately 16.9-17.2 FPS.

## Final layout

The tracked result directory will contain one official demonstration video:

```text
results/jetson/2026-08-30/jetson_demo.mp4
```

The two superseded tracked videos will move to the ignored local backup directory:

```text
backups/jetson/2026-08-30/superseded-mp4/jetson_demo_01.mp4
backups/jetson/2026-08-30/superseded-mp4/jetson_demo_02.mp4
```

They remain recoverable both from the local backup directory and from earlier Git
commits. Removing them from the current snapshot does not remove their blobs from
existing Git history and therefore does not retroactively reduce repository history
size.

## Documentation updates

- `README.md` will link only to `jetson_demo.mp4` as the final demonstration.
- `results/jetson/2026-08-30/README.md` will replace the two old media entries with
  the verified metadata, SHA256, and visual-check summary for the combined video.
- `models/MODEL_CARD.md` already links to the Jetson result directory and requires no
  filename-specific change.
- The earlier integration design remains a historical design record; this new design
  documents the later user-selected replacement.

## Git behavior

- Move the selected video into the tracked result directory without transcoding it.
- Record the two old tracked videos as deletions and the selected video as an
  addition.
- Commit the video replacement and documentation changes together as:
  `media: replace Jetson demos with final video`.
- Push normally to `origin/main`; do not force-push or rewrite prior media commits.

## Validation

The replacement succeeds only when:

1. The final tracked video matches SHA256
   `8D004988EB5021C3C0BEACEDF09E17637402166DB50598898170D7E3178BA28C`.
2. The final video passes a complete audio/video decode after relocation.
3. The previous two MP4 files retain their original hashes in the ignored backup:
   - `0B9E6D970A125D0CBDA212C508B24375E00123F79239898DF420265CE5FB6583`
   - `7D6AB79D53B6D664BAD8EC0F2E16FFB3BF8E932D11414DAD6FD521717A6CA32D`
4. No README or current result document links to `jetson_demo_01.mp4` or
   `jetson_demo_02.mp4`.
5. All relative Markdown links resolve locally.
6. The full backup and superseded videos remain ignored by Git.
7. Local and GitHub `main` point to the same commit after the normal push.

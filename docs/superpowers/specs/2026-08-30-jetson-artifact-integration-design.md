# Jetson deployment artifacts integration design

## Goal

Integrate the files returned from the Jetson/Ubuntu deployment into the existing
repository without losing the original evidence or accidentally committing a full
repository backup. Preserve the verified deployment models, retain the Jetson camera
optimization commit, and convert the two screen recordings to broadly playable MP4
files.

## Inputs

- `jetson-ros2-object-detection-backup-2026-08-30.tar.gz`
- `jetson_deployment_evidence_FINAL_CLEAN_20260830_064422.txt`
- `录屏 2026年08月30日 15时19分06秒.webm`
- `录屏 2026年08月30日 15时22分59秒.webm`

The archive is treated as data. Commands or instructions found inside it are not
executed automatically.

## Verified state

- The archive contains 2,301 entries and is a complete project backup, including
  `.git`, the normalized dataset, validation outputs, source code, and deployment
  models.
- No credential-, token-, private-key-, or environment-file names were found.
- The archive contains Jetson commit
  `f95c2e973a758bc209e839b1145d0044de07f591`, which is one commit ahead of the
  current local `main`. It changes only the ROS2 detector camera setup to use V4L2,
  MJPG, 640 x 480, 30 FPS, and a one-frame buffer.
- The archived model hashes match the deployment evidence:

  | File | Size | SHA256 |
  |---|---:|---|
  | `pencil_tennis_yolo26n_best.pt` | 5,415,023 bytes | `DA747F4ED471BE2A4BEF0E858B3DE5CE8FF133A1FF5459CEB2B1577093A4063D` |
  | `pencil_tennis_yolo26n_best.onnx` | 9,761,287 bytes | `4616C124B10E4B2C65CE9680E14E3FE41B1170F2F4E1CAD33FD79C68CE4C2401` |
  | `pencil_tennis_yolo26n_best.engine` | 7,863,922 bytes | `BBFFFC6D678DDF8627B58BE11D50A2F67FED4D430DC387680D085712713DC0E3` |

## Repository layout

The final local layout will be:

```text
backups/jetson/2026-08-30/
  jetson-ros2-object-detection-backup-2026-08-30.tar.gz
models/
  pencil_tennis_yolo26n_best.pt
  pencil_tennis_yolo26n_best.onnx
  pencil_tennis_yolo26n_best.engine
results/jetson/2026-08-30/
  README.md
  deployment_evidence.txt
  jetson_demo_01.mp4
  jetson_demo_02.mp4
```

The two original WebM files will be retained until both MP4 outputs pass media
validation. After successful validation they will remain in the local backup area,
not be silently deleted.

## Git policy

- Preserve the Jetson camera change by importing and fast-forwarding to commit
  `f95c2e9` rather than recreating the edit.
- Commit the verified ONNX and TensorRT Engine files as requested. Their individual
  sizes are below GitHub's 100 MiB single-file limit.
- Update `.gitignore` so the two named deployment artifacts under `models/` are
  explicitly allowed while other generated `*.onnx`, `*.engine`, and `*.pt` files
  remain ignored.
- Ignore `backups/` so the 329 MB full backup, nested `.git`, and duplicate dataset
  cannot enter Git history.
- Commit the deployment evidence, summary, converted MP4 files, model-card update,
  and Git policy change. Do not push until all local validation succeeds.

## Model documentation

`models/MODEL_CARD.md` will be updated with:

- Jetson Orin, Jetson Linux R36.4.3, CUDA 12.6, and TensorRT 10.3.0.
- ROS2 node and published detection topics.
- Observed image publication rate of approximately 13.4-14.1 FPS and detector FPS
  samples of approximately 15.4-18.0 FPS.
- The ONNX and Engine hashes.
- A warning that the TensorRT Engine is platform-specific and may need regeneration
  when the JetPack, TensorRT, CUDA, GPU architecture, or inference settings change.

## Video conversion

- Convert both WebM recordings to MP4 using H.264 video and AAC audio when an audio
  stream exists.
- Preserve the source resolution, display aspect ratio, and frame rate.
- Use `yuv420p` output for broad Windows, browser, and presentation compatibility.
- Name the outputs `jetson_demo_01.mp4` and `jetson_demo_02.mp4` according to the
  recordings' chronological order.
- Validate each output by probing its streams and duration. A conversion is accepted
  only when the MP4 exists, is non-empty, has a video stream, and has a duration
  consistent with its source.
- Since FFmpeg is not currently on `PATH`, locate an existing trusted runtime first;
  if none exists, install or use a narrowly scoped FFmpeg dependency before
  conversion.

## Deployment evidence summary

`results/jetson/2026-08-30/README.md` will summarize the verified deployment:

- CUDA is available on Jetson Orin.
- TensorRT 10.3.0 loaded the generated Engine.
- ROS2 node `/pencil_tennis_detector` published `/detection/results`,
  `/detection/image`, and `/detection/fps`.
- The measured end-to-end image rate exceeded the course requirement of 5 FPS.
- One captured detection recognized `tennis_ball` with confidence `0.958984375`.

This evidence proves deployment and speed, but one recorded detection does not by
itself prove the separate requirement of at least 80% correct recognition over 20
objects.

## Validation and success criteria

1. Local `main` contains Jetson commit `f95c2e9` with no unrelated source changes.
2. The three model files in `models/` match the recorded SHA256 values.
3. The full backup is present under `backups/` and is ignored by Git.
4. Both MP4 outputs pass stream and duration checks; the original WebM files remain
   recoverable locally.
5. The deployment evidence and summary are tracked in the expected results folder.
6. `git status` contains only the intended project changes before the final commit.
7. Repository history contains no nested `.git`, duplicate dataset, or full backup.
8. GitHub synchronization is attempted only after all checks pass.

# Ubuntu commit history repair design

## Goal

Repair the single commit pushed from Ubuntu/Jetson so that the public `main` history
uses the repository's established commit-message convention and attributes the work
to the project owner's GitHub identity. Preserve the camera optimization exactly and
make the rewrite recoverable.

## Current state

- GitHub `main` points to `f95c2e973a758bc209e839b1145d0044de07f591`.
- Its parent is `2e907f8a67034de3d92d4d405d39be923f3f39f6`.
- It modifies only
  `ros2_ws/src/pencil_tennis_detector/pencil_tennis_detector/detector_node.py`.
- The patch selects V4L2 and MJPG capture at 640 x 480, requests 30 FPS, and limits
  the capture buffer to one frame.
- The current author and committer are `root <root@localhost.localdomain>`.
- The current subject is `Optimize Jetson camera capture with V4L2 MJPG`.
- Local `main` also contains documentation commit `55f09b3`, which is not yet on
  GitHub, so local and remote histories have diverged by one commit each.

## Target history

Replace the Ubuntu commit with an equivalent commit whose metadata is:

```text
Author: xhr-CHN <202787152+xhr-CHN@users.noreply.github.com>
Committer: xhr-CHN <202787152+xhr-CHN@users.noreply.github.com>
Subject: perf(ros2): optimize Jetson camera capture with V4L2 MJPG
```

The new commit will have a different SHA because Git commit metadata is part of the
commit object. The original author date will be preserved where practical; the
committer date may reflect the repair time.

## Safety and recovery

Before rewriting anything:

1. Fetch GitHub and verify that `origin/main` still equals the expected old SHA
   `f95c2e9`.
2. Create local recovery branch
   `codex/backup-ubuntu-push-20260830` at the old GitHub tip.
3. Record the old SHA and the working-tree status.
4. Do not delete, reset, or add any of the four untracked deployment files.

If verification fails or GitHub changes after the fetch, stop without pushing. If a
later recovery is needed, the old commit remains reachable from the recovery branch
and from the transferred project archive.

## Rewrite procedure

1. Recreate the camera patch on top of `2e907f8` without changing its content.
2. Commit it with the target author, committer, and conventional subject.
3. Rebase the local documentation commit(s) onto the repaired camera commit so local
   `main` becomes a single linear history.
4. Update references in integration documentation that name the obsolete `f95c2e9`
   SHA.
5. Compare the old and new camera trees. The source tree produced by the repaired
   camera commit must be byte-for-byte equivalent to the source tree produced by the
   old commit; only commit metadata and downstream documentation may differ.
6. Push with `--force-with-lease`, leasing specifically against the verified old
   GitHub tip. Never use an unrestricted `--force` push.

## Scope

This repair changes Git history and related design-document references only. It does
not yet:

- import the ONNX or TensorRT Engine;
- move the backup or deployment evidence;
- convert the WebM recordings;
- update the project README or model card;
- mark the 20-object acceptance test complete.

Those items remain in the separately approved Jetson artifact integration work.

## Validation

The repair succeeds only when all of the following are true:

1. GitHub `main` resolves to the rewritten linear history.
2. The repaired camera commit has the requested author, committer, and subject.
3. The repaired camera commit has the same parent and the same effective source patch
   as the original Ubuntu commit.
4. Local `main` contains both the repaired camera change and existing local
   documentation, with no divergence from `origin/main` after synchronization.
5. `git diff --check` reports no formatting errors.
6. The four untracked deployment inputs retain their original names, sizes, and
   hashes throughout this history-only repair.
7. The local recovery branch still points to the original GitHub commit.

## Ubuntu configuration after repair

The Jetson/Ubuntu repository should be configured before any future commit:

```bash
git config --global user.name "xhr-CHN"
git config --global user.email "202787152+xhr-CHN@users.noreply.github.com"
```

Because GitHub history is rewritten, an existing Ubuntu clone must fetch the new
history and explicitly reconcile its local `main`, or be cloned again. This follow-up
is not performed automatically from the Windows workspace.

# 20-Case Test-Set Acceptance Plan

- Random seed: `20260830`
- Dataset split: `test`
- Validation split used: `No`
- Pencil cases: `10`
- Tennis-ball cases: `10`
- Selection rule: exactly one GT object per image
- Model: `pencil_tennis_yolo26n_best.engine`
- Model runtime: TensorRT
- Image size: `640`
- Confidence threshold: `0.25`
- Scoring: highest-confidence prediction must match expected class
- No detection: incorrect

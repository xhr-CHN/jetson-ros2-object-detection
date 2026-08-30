# Acceptance Errors

## Test 03

- Global GT object ID: 70
- Image: `pencil_red4.jpg`
- Expected class: `pencil`
- Predicted class: `none`
- Confidence: 0.000000
- Offline model FPS: 31.16
- Prediction count: 0
- Possible cause: requires manual review of the saved annotated image.


## Manual review note

The failed case is retained without replacement or re-sampling.

- Acceptance ID: 03
- Global GT object ID: 70
- Image: `pencil_red4.jpg`
- Expected class: `pencil`
- Predicted class: `none`
- Confidence: `0.000000`
- Prediction count: `0`

The deployed TensorRT model produced no detection above the configured
confidence threshold of 0.25 for this image. Therefore this case is scored
as an incorrect detection (false negative / missed detection).

No failed record was deleted or manually changed.

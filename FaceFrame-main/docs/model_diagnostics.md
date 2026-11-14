# FaceFrame Model Diagnostics and Viability Notes

## Startup context checked

FaceFrame's public site positions the product as an AI eyewear-shopping assistant that scans a user's face, classifies face shape, recommends frames, and supports virtual try-on. That makes the face-shape model a discovery and personalization component, not a medical or biometric identity system. For the startup to be viable, the model should be evaluated on whether it reliably improves frame selection, fit confidence, and conversion for real shoppers across lighting, device, demographic, and store conditions.

## Current model and validation setup

- The active CNN training script builds a four-class face-shape classifier for `heart`, `oval`, `round`, and `square` labels.
- Images are first assigned to class folders from `src/data/cluster_results.json`, where cluster IDs are mapped directly to face-shape labels.
- The CNN input is a `128 x 128 x 4` tensor: three color channels after CLAHE contrast enhancement plus a Canny edge-map channel.
- Training uses a random 80/20 stratified split from `src/data/sorted_images`, early stopping, and model checkpointing.
- The evaluator reports validation loss, validation accuracy, a classification report, and a confusion matrix using the saved H5 model.

## Dataset snapshot

Current sorted validation/training pool size is 2,151 images:

| Class | Images | Share |
| --- | ---: | ---: |
| square | 703 | 32.7% |
| round | 626 | 29.1% |
| heart | 443 | 20.6% |
| oval | 379 | 17.6% |

Critical note: this is not severely imbalanced, but it is still skewed enough that plain accuracy can look better than the actual user experience for the smaller `oval` and `heart` classes. Macro F1, per-class recall, and confusion by class should be treated as first-class metrics.

## Accuracy and validation reliability concerns

The current validation accuracy should be treated as an internal smoke-test metric, not as proof of production accuracy. The biggest risks are:

1. **Weak ground truth.** Labels appear to come from cluster assignments that are manually mapped to face-shape names. Unless those clusters were independently audited by humans or opticians, the model may be learning cluster artifacts rather than true face-shape semantics.
2. **Validation leakage risk.** The train/validation split is random at the image-file level. If the dataset contains near-duplicates, same-person images, or images from the same source session, validation accuracy can be inflated. A production-quality test must split by person, capture session, or source.
3. **Evaluator preprocessing mismatch.** The training pipeline uses CLAHE plus Canny to create a fourth channel. The current evaluator loads images directly as RGBA-like data. That means the reported evaluation may not match the training/inference feature distribution and can understate or overstate true quality.
4. **No confidence calibration.** The product needs to know when not to trust itself. A high softmax score is not automatically a reliable probability. FaceFrame should measure expected calibration error and set abstention thresholds for uncertain scans.
5. **No real-world validation set.** Store/kiosk and webcam images can differ from curated images because of lighting, pose, camera quality, hair, hats, facial hair, skin tone, lens glare, and occlusion. The model needs a holdout set collected from the actual product flow.
6. **Face shape may be an ambiguous label.** Face shapes are continuous and subjective. Many users sit between categories. A single-label classifier may create poor recommendations for borderline users; top-2 shape predictions or continuous facial measurements may be more useful.
7. **Business metric is not model accuracy.** The model is only viable if it improves shopper outcomes: faster selection, higher try-on engagement, higher add-to-cart rate, fewer returns, better satisfaction, and retailer lift.

## What accuracy would be good enough?

For an early MVP, validation accuracy is only useful if paired with evidence that recommendations feel correct to users. Suggested gates:

- **Internal MVP:** macro F1 above 0.75 on a deduplicated, person-level holdout set, with no class recall below 0.65.
- **Pilot with retailers:** macro F1 above 0.80 on store/kiosk images plus measured recommendation satisfaction above a non-AI baseline.
- **Commercial readiness:** model confidence calibration, fairness slices, repeated-device testing, and A/B evidence that AI recommendations improve conversion or reduce selection time.

These thresholds are product-oriented suggestions, not guarantees. If the recommendation layer can recover from an imperfect face-shape prediction by using top-2 predictions and style preferences, lower classifier accuracy may still be commercially viable.

## Future improvements required

1. **Create a real evaluation dataset.** Collect consented user scans from the intended kiosk/webcam/mobile flow and label them independently. Keep this set locked and never train on it.
2. **Use person-level splitting.** Ensure all images of the same person stay in only train, validation, or test.
3. **Fix preprocessing parity.** Refactor preprocessing into a shared function used by training, evaluation, and live inference.
4. **Report richer metrics.** Save accuracy, macro/micro/weighted F1, per-class precision/recall, confusion matrix, top-2 accuracy, confidence histograms, and low-confidence abstention rate.
5. **Evaluate fairness and robustness.** Slice by lighting, camera, skin tone, gender presentation, age range, facial hair, glasses already worn, head pose, and occlusion.
6. **Move beyond categorical face shape.** Add geometric facial measurements from MediaPipe landmarks, such as face length/width ratio, jaw width, cheekbone width, forehead width, and nose bridge fit. These measurements may map more directly to frame fit than a four-way class.
7. **Validate frame recommendations directly.** Ask users or opticians to rate recommended frames, not just predicted face shapes. The startup wins on frame fit and confidence, not classifier leaderboard scores.
8. **Add monitoring.** Track production confidence, failed scans, class distribution drift, return rates, and user feedback by model version.

## Recommended next diagnostic work

- Run the evaluator in a fully provisioned Python environment with `requirements.txt` installed.
- Add a reproducible metrics artifact under `reports/` for every model version.
- Build a small manually reviewed test set of at least 100 users per class before using validation accuracy in investor or customer-facing claims.
- Compare three baselines: majority-class prediction, landmark-ratio rules, and the CNN. If the CNN does not beat simple landmark features on real scans, prioritize data quality and feature design before scaling model complexity.

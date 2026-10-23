# Split overlap screening — Stationery v7

## Outcome
The original uploaded dataset contains cross-split images with strongly matching visual content. Passing a SHA-256 duplicate check does not establish split independence. No images, labels, or splits were changed in this audit.

A perceptual screening produced 26 candidate pairs. Contact-sheet inspection identified four especially strong matches in composition (pairs 1, 2, 4, and 8). Other candidates include different objects with similar layouts and likely related captures; candidate status alone does not establish duplication.

## Scope
- Original export: stationery.v7i.yolov8.zip, version 7, YOLOv8.
- Images decoded successfully: train 2,268; validation 111; test 206.
- Decode errors: 0.
- Compared 741,822 pairs across different splits.
- Byte-identical cross-split image groups: 0.
- Exact source filename-prefix overlap before `.rf.`: 0 groups. This literal test misses changes such as added `_jpg` suffixes and renamed files.
- Source ZIP SHA-256: `ee4bcdefef2ebcf202b6cc1d783db681a67271491da83c747b696eba037663a0`.

## Method
Decoded each image with Pillow, converted to grayscale, and computed a 64-bit difference hash (9 by 8 pixels). For each pair across splits, compared one image's hash against eight rotations/reflections of the other. Flagged a pair when the smallest Hamming distance was at most 4. Inspected the two accompanying contact sheets.

Difference hashes are a heuristic. Matching hashes can be false positives, especially for simple pencil/ruler layouts. Different hashes can miss related photos, crops, or mosaic reuse. Rotation/flip checks do not cover arbitrary crops or complex augmentation.

## Strong visual matches
Pair numbers match the contact sheets. These are visual similarity judgments, not claims that file bytes are identical.

### Pair 1

- `train/images/292_jpg.rf.faf51b390f1271d6538dd749b1c221fd.jpg`
- `test/images/171_jpg.rf.bb195a6f4797b5e12a6e2f0d1e31ec54.jpg`
- Difference-hash distance: 0.

### Pair 2

- `train/images/378977_1.rf.f688e98e06c91622d6ef786dce33bc5a.jpg`
- `valid/images/378977_1_jpg.rf.fff928a7f5ed3c60a0ca4e49ab844496.jpg`
- Difference-hash distance: 0.

### Pair 4

- `valid/images/83.rf.cb0969d9a243b31a5845c49a6cf8f39c.jpg`
- `test/images/83_jpg.rf.5dd73a08f5803619652c6511b52f3c04.jpg`
- Difference-hash distance: 0.

### Pair 8

- `train/images/73_jpg.rf.416de1b3584310429fcdae8e19372f06.jpg`
- `test/images/92_jpg.rf.41293faead90c286efdfe5f6ffdcc935.jpg`
- Difference-hash distance: 2.

## Recommended next steps
1. Review the four strong matches at original resolution and record a source-group decision before training or final evaluation.
2. Keep every confirmed source image and its augmented variants within a single split. Inspect related filenames/variants as part of each group, rather than moving just one candidate image.
3. Establish provenance for mosaic images where possible; shared source pixels can create leakage even when filenames differ.
4. Keep a log of all split changes and regenerate counts/configuration after any change.
5. Re-run the format/pairing checker and overlap screening after changes.
6. Treat final model evaluation as pending until the group has resolved and documented split independence to the extent supported by available provenance.

This is an initial screening, not proof that every related image has been identified. Do not automatically delete all 26 candidate pairs. Training-label cleanup is separate from split changes.

## Reproduce
The included audit_split_overlap.py reads the original ZIP. It requires Python and Pillow. Install Pillow in the environment used to run the script, then run:

```bat
py -m pip install Pillow
py audit_split_overlap.py stationery.v7i.yolov8.zip --output split_overlap_results.json
```

The script only reads the ZIP and writes a JSON report. It does not edit the dataset. The two contact sheets supplied here were produced during this review; rerunning the script produces the numeric candidate report only. Pillow versions/resampling can affect borderline candidate distances. Four strong matches were selected by visual inspection rather than automatically by the script.

## Credit
Dataset: Stationery v7 by Lalaworkspace, CC BY 4.0.
https://universe.roboflow.com/lalaworkspace/stationery-l7qrn/dataset/7
The contact sheets resize and arrange dataset images with pair labels added.

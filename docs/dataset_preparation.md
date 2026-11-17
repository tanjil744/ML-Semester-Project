# Dataset preparation and training handoff

## Current handoff snapshot

Use the **Grouped Stationery Dataset v1.0**
[release](https://github.com/tanjil744/ML-Semester-Project/releases/tag/dataset-grouped-v1.0)
and its `stationery_grouped_for_training.zip` attachment for the exact
handoff snapshot.

| Split | Images | Label files |
| --- | ---: | ---: |
| train | 2,284 | 2,284 |
| valid | 103 | 103 |
| test | 198 | 198 |
| Total | 2,585 | 2,585 |

The original export had 2,268 / 111 / 206 images. The first reviewed copy
had 2,271 / 111 / 203; the grouped copy has the counts above. All versions
include augmented images.

The published dataset attachment has SHA-256:

```text
e6bcf4a63761000292ef12209eb202462f4bdcdda59ffc0348be548a0ab3cf20
```

### Configure training after extracting

Set `path:` in the extracted dataset's `data.yaml` to the extracted
`stationery.v7i.yolov8_grouped` folder in your environment. The remaining
split fields are:

```yaml
train: train/images
val: valid/images
test: test/images
nc: 4
names: ['eraser', 'pencil', 'pencil sharpener', 'ruler']
```

Keep the class IDs unchanged. Pass this extracted configuration to the
training script and label the experiment `dataset-grouped-v1.0`.
Training uses train; tuning and model selection use valid; final evaluation
uses test. Earlier results recorded with the original split should retain
that dataset-version label.

## Source and credit

Stationery dataset, version 7, by Lalaworkspace; license CC BY 4.0.
[Original source](https://universe.roboflow.com/lalaworkspace/stationery-l7qrn/dataset/7).

Original images and annotations are credited to the creator. Our group
changed label formatting, removed duplicate annotations, restored one missing
local sharpener annotation, and grouped reviewed related captures within
splits. The release remains a prepared derivative of the source dataset.

## Reproduce the preparation procedure

The following Windows Command Prompt workflow starts from the original
version-7 YOLOv8 export, not from the already prepared release. Use the
release ZIP when you need the exact handoff snapshot.

1. Extract the original download into `stationery.v7i.yolov8`.
2. Download the five Python files from [scripts](../scripts/) into the
   parent directory of that folder.
3. Open Command Prompt in that parent directory. Keep the original folder,
   generated copies, and backups as sibling folders.

### 1. Audit and clean annotations

```bat
py check_dataset.py stationery.v7i.yolov8 > audit_original_format.txt
py prepare_detection_labels.py stationery.v7i.yolov8
py check_dataset.py stationery.v7i.yolov8 > audit_cleaned_format.txt
```

The cleanup validates labels, converts polygons to enclosing bounding boxes,
removes equal duplicate annotations, saves original affected files in a
timestamped backup, and records changes in `changes.json`.

The original audit flagged seven polygon lines and ten duplicate annotation
lines. During the historical manual workflow, three polygons were fixed
first; the cleanup then handled four polygons and ten duplicates across
11 remaining files. Starting from the original export, the script handles
all seven polygon conversions without repeating those manual edits.
The later missing local sharpener line was restored from the original
annotation; it is already present in the original export.

### 2. Group the first four reviewed source families

Preview, then create a separate reviewed copy:

```bat
py prepare_reviewed_splits.py stationery.v7i.yolov8
py prepare_reviewed_splits.py stationery.v7i.yolov8 --apply
```

Expected output folder: `stationery.v7i.yolov8_reviewed_splits`.
Expected image/label counts: train 2,271; valid 111; test 203.
Four image–label pairs are relocated; reviewed image contents are verified
against the recorded source hashes.

### 3. Add the reviewed capture groups

```bat
py prepare_additional_groups.py stationery.v7i.yolov8_reviewed_splits
py prepare_additional_groups.py stationery.v7i.yolov8_reviewed_splits --apply
```

Expected output folder: `stationery.v7i.yolov8_grouped`.
Fourteen additional image–label pairs are relocated. Seven reviewed groups
cover 119 known images, including named training mosaics. Image and label
contents are preserved during grouping. The new `split_corrections.json`
retains the previous log and the 22-candidate visual-review decisions.

Group 101 treats the dated image sequence as a conservative capture-session
group, inferred from filenames and visual context. Groups 102 and 103 handle
the two reviewed red-pencil families. This is not verified provenance for
every image in the dataset.

Both grouping scripts create new copies and refuse to overwrite an existing
output folder. Use a fresh output directory with `--output` when repeating
a preparation run.

### 4. Verify the grouped copy

```bat
py check_dataset.py stationery.v7i.yolov8_grouped > dataset_check_after_grouping.txt
py -m pip install Pillow
py audit_reviewed_overlap.py stationery.v7i.yolov8_grouped --output split_overlap_after_grouping.json
```

The overlap auditor writes a JSON report outside the dataset and leaves
images and labels unchanged. Choose a new report filename if the output
already exists.

## Recorded outcomes and limits

- [Grouped format/pairing audit](dataset_check_after_grouping.txt): zero
  issues under the implemented checks.
- [Grouped correction log](split_corrections_after_grouping.json): seven
  reviewed groups and fourteen additional paired moves; the earlier log
  records the first four moves.
- Recorded overlap run: 2,585 decoded images, zero decode errors,
  707,878 cross-split comparisons, zero byte-identical cross-split groups,
  zero normalized-filename cross-split groups, and seven of seven
  reviewed groups passing.
- Twelve remaining perceptual candidates were visually reviewed; that
  review did not establish a shared original source strongly enough to
  justify further moves.
- The [initial overlap review](split_overlap_review.md) records the
  earlier 26-candidate screening. Candidate numbering can differ between
  runs; identify images by their full filenames.
- The [empty-label review](empty_label_review.md) provisionally retained
  the 19 empty labels; it did not establish exhaustive annotation accuracy.

Perceptual hashes can both miss related captures and flag different images
with similar layouts. Crop reuse and mixed-source mosaics are not fully
covered; complete source independence and visual correctness of every
annotation are not established. Pillow versions can affect borderline
candidate distances. These checks do not establish detection accuracy or
package-level performance.

## Next model work

Use the grouped release for a new, clearly versioned training/evaluation
run. Evaluate actual assembled kits with known item counts to assess
package-completeness decisions. Record detection metrics separately from
the correctness of complete/missing/excess package decisions.

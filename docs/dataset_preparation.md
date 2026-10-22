# Dataset Preparation

## Source and credit
Stationery dataset, version 7, by Lalaworkspace.
License: CC BY 4.0.
https://universe.roboflow.com/lalaworkspace/stationery-l7qrn/dataset/7

Our group modified label formatting and removed duplicate annotations.
The original images and annotations are credited to the dataset creator.

## Download
Download version 7 in YOLOv8 format and extract the ZIP.

Keep an original copy before preparing the dataset.

## Class mapping
- 0: eraser
- 1: pencil
- 2: pencil sharpener
- 3: ruler

Preserve this mapping. The inspection target is 2 pencils,
1 eraser, and 1 ruler.

## Reproduce the cleanup
Download these files from our repository's scripts folder:
- check_dataset.py
- prepare_detection_labels.py

Place both scripts beside the extracted stationery.v7i.yolov8 folder.
Open a terminal in that parent folder.

Run the initial audit:

```bat
py check_dataset.py stationery.v7i.yolov8 > audit_before.txt
```

Run the cleanup:

```bat
py prepare_detection_labels.py stationery.v7i.yolov8
```

Run the audit again:

```bat
py check_dataset.py stationery.v7i.yolov8 > audit_after.txt
```

The cleanup script:
- Converts polygon annotations into enclosing rectangular boxes.
- Removes repeated annotations with identical class and box coordinates.
- Backs up affected labels in a timestamped Label_Backup folder.
- Records changes in changes.json.
- Preserves images and the existing dataset splits.

Starting from the original download, the script handles all
corrections; teammates do not need to repeat the manual edits below.

## Work performed
The initial audit flagged 17 annotation lines:
- 7 polygon annotations requiring conversion for box detection.
- 10 duplicate annotations.

Three polygon annotations were converted manually first.
The cleanup script then changed 11 remaining files, converting
4 polygons and removing 10 duplicate annotations.

The final audit reported 0 file and annotation issues under
the checks implemented in check_dataset.py.

## Dataset size
- Training: 2,268 images
- Validation: 111 images
- Test: 206 images
- Total: 2,585 images, including augmented images

## Remaining review
- Inspect the 19 empty label files for missing annotations.
- Visually check bounding boxes and class assignments.
- Check similar and augmented images for overlap between splits.
- Confirm image paths for the training environment.
- Evaluate package completeness using images with known item counts.

Zero issues in the automated report establishes format consistency
under those checks. It does not establish visual annotation accuracy,
independent dataset splits, or model performance.

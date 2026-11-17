# Stationery Package Inspection

Group machine learning semester project — Fall 2026.

Detect and count stationery in an open package image, then check the required
contents: **2 pencils, 1 eraser, and 1 ruler**. A pencil sharpener is also
detected but is not a required item in the current kit specification.

## Prepared dataset: grouped v1.0

Download **stationery_grouped_for_training.zip** from the
[dataset release](https://github.com/tanjil744/ML-Semester-Project/releases/tag/dataset-grouped-v1.0).
The named dataset attachment contains the images, labels, configuration, and
split correction log.

| Split | Images | Label files |
| --- | ---: | ---: |
| Training | 2,284 | 2,284 |
| Validation | 103 | 103 |
| Test | 198 | 198 |
| Total | 2,585 | 2,585 |

Counts include augmented images. The original Roboflow export used
2,268 / 111 / 206 images; the grouped release changes split assignments
while preserving the total image count.

### Class mapping

| ID | Class |
| --- | --- |
| 0 | eraser |
| 1 | pencil |
| 2 | pencil sharpener |
| 3 | ruler |

### Recorded checks and limits

- Zero file-format or image–label pairing issues in the
  [grouped dataset audit](docs/dataset_check_after_grouping.txt).
- All 2,585 images decoded successfully in the recorded overlap screening.
- All seven reviewed source/capture groups passed the grouping check.
- Twelve perceptual-hash candidate pairs remained. Their visual review did
  not establish a shared source strongly enough to justify further moves.
- Complete source independence, provenance of all mosaic components, and
  visual correctness of every annotation are not established.

These checks describe dataset preparation; they are not model performance
results or a package-level accuracy benchmark.

## Training handoff

1. Download and extract the named dataset ZIP from the release.
2. Set `path:` in the extracted dataset's `data.yaml` to its folder on your
   own computer or Colab.
3. Pass that configuration to the training code and identify the dataset
   version as `dataset-grouped-v1.0` in the run records.
4. Train on the 2,284 training images, select settings on the 103 validation
   images, and evaluate the selected model on the 198 test images.

The [training README](model_training/README.md) currently describes the
original split sizes. Confirm the dataset version when comparing its results
with a grouped-dataset run. Package inspection also needs evaluation on
assembled kits with known complete, missing-item, and excess-item contents.

## Dataset preparation

See the [preparation and reproduction guide](docs/dataset_preparation.md)
and [annotation guidelines](docs/annotation_guidelines.md).

| Script | Purpose |
| --- | --- |
| [check_dataset.py](scripts/check_dataset.py) | Check label format, coordinates, image–label pairing, duplicate annotations, and byte-identical images. |
| [prepare_detection_labels.py](scripts/prepare_detection_labels.py) | Convert polygons to enclosing boxes and remove duplicate annotations, with backups. |
| [prepare_reviewed_splits.py](scripts/prepare_reviewed_splits.py) | Create a new copy with the first four reviewed source groups colocated. |
| [prepare_additional_groups.py](scripts/prepare_additional_groups.py) | Create the grouped copy, retaining the first four groups and adding three reviewed capture groups. |
| [audit_reviewed_overlap.py](scripts/audit_reviewed_overlap.py) | Decode images, screen cross-split similarity, and verify the recorded reviewed groups. |

Earlier audit reports remain in `docs/` as preparation history. The
[current correction log](docs/split_corrections_after_grouping.json) retains
the earlier log and records the additional grouping decisions.

Other project components: [model training](model_training/),
[inspection logic](Inspection/), and [app](app/).

## Dataset source and credit

Original dataset: **Stationery v7 by Lalaworkspace**,
[Roboflow source](https://universe.roboflow.com/lalaworkspace/stationery-l7qrn/dataset/7).
License: **CC BY 4.0**. Original images and annotations are credited to the
dataset creator. Our preparation changed annotation formatting, removed
duplicate annotations, restored a missing local annotation, and changed
reviewed split assignments.

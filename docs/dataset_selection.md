# Dataset Selection and Preparation

## Project goal
Build a computer vision prototype that detects stationery items
and checks whether a package contains 2 pencils, 1 eraser, and 1 ruler.

## Selected dataset
- Name: Stationery
- Creator: Lalaworkspace
- Platform: Roboflow Universe
- Version: 7
- Format: YOLOv8 object detection
- License: CC BY 4.0
- Source: https://universe.roboflow.com/lalaworkspace/stationery-l7qrn/dataset/7

The dataset and original annotations belong to their credited creator.
Our group is using this public dataset as a starting point.

## Why this dataset was selected
It includes all three objects required for our project:
pencils, erasers, and rulers. It also provides bounding-box
annotations and existing training, validation, and test folders,
making it practical for a semester project.

A fourth class, pencil sharpener, is included. We will preserve
the original four-class mapping during initial dataset preparation.

## Dataset contents
| Split | Images |
| --- | ---: |
| Training | 2,268 |
| Validation | 111 |
| Test | 206 |
| Total | 2,585 |

The total includes augmented images, so it does not represent
2,585 independent original photographs.

## Class mapping
| Class ID | Object |
| --- | --- |
| 0 | eraser |
| 1 | pencil |
| 2 | pencil sharpener |
| 3 | ruler |

## Preprocessing documented by the dataset creator
- Automatic image orientation
- Resizing to 640 × 640 pixels using stretching

## Augmentation documented by the dataset creator
- Horizontal and vertical flips
- 90-degree rotations
- Exposure adjustments

## Work completed
- Practiced drawing bounding boxes using Make Sense.
- Exported practice annotations in YOLO format.
- Checked the practice export's class mapping.
- Downloaded and extracted the selected dataset.
- Reviewed data.yaml and the included README files.
- Documented the dataset source and download instructions
  in the project README.

## Limitations and pending checks
- Annotation accuracy and completeness still need review.
- Duplicate and related images across splits still need checking.
- Class balance and bounding-box validity still need checking.
- General stationery photos may differ from actual package images.
- Package completeness performance requires separate evaluation
  on images with known item counts.
- No model performance or accuracy has been established yet.

## Next steps
1. Check image-label pairing and annotation validity.
2. Count examples of each class.
3. Check for duplicates across dataset splits.
4. Visually review a sample of annotated images.
5. Record findings and share the reviewed dataset with the
   model-training teammate.

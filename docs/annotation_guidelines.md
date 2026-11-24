# Annotation Guidelines

## Purpose
Use consistent bounding-box labels when reviewing the downloaded
dataset or adding new images.

## Class IDs
Follow the downloaded dataset's data.yaml:

| ID | Label |
| --- | --- |
| 0 | eraser |
| 1 | pencil |
| 2 | pencil sharpener |
| 3 | ruler |

Pens must not be labeled as pencils.

## Bounding-box rules
- Draw one rectangle around each individual object.
- Keep boxes tight around the object's visible extent.
- Include the full object when it is fully visible.
- Do not put multiple objects inside one shared box.
- Label every identifiable instance of the four target classes.
- For partially hidden objects, box the visible extent consistently.
- Flag objects that cannot be identified confidently for team review.
- Do not guess the class of an unclear object.

## YOLO label format
Each image has a matching text file with the same base filename:
- example.jpg
- example.txt

Each object occupies one line:
class_id x_center y_center width height

Coordinates are normalized relative to image dimensions.
Class IDs must be integers from 0 to 3.
Box width and height must be greater than zero.
Boxes must remain within the image boundaries.

## Package inspection
A complete package requires:
- 2 pencils
- 1 eraser
- 1 ruler

Object labels describe what is visible, even if an item is extra
or the package is incomplete. Package pass/fail decisions are
handled separately by the inspection logic.

## Review checklist
- Every image has its corresponding label file.
- All identifiable target objects are labeled.
- Labels match the objects.
- Boxes fit the objects.
- No accidental duplicate boxes exist.
- Unclear cases are recorded for review.

## Practice export
The initial Make Sense practice used:
0 = eraser, 1 = pencil, 2 = ruler.

The downloaded dataset uses 3 = ruler.
Do not merge the practice labels into this dataset without
remapping IDs and completing all missing annotations.

## Status
These are our team's proposed rules for review and future labeling.
The downloaded annotations have not yet been fully checked
against these rules.

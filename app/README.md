# Packaging Quality Inspection App

## Overview
This application uses a YOLO object detection model to inspect stationery packages.

## Expected Package
- 2 pencils
- 1 eraser
- 1 ruler

## Requirements
Python 3.10 or a compatible version, the required Python libraries, and trained YOLO model weights (`best.pt`).

Install dependencies from the project root:

```bash
python -m pip install -r requirements.txt
```

## Run the Application
From the project root, run:

```bash
python -m streamlit run app/app.py
```

## Usage
1. Start the application.
2. Upload a JPG, JPEG, or PNG package image.
3. Check the model weights path in the sidebar.
4. Select the confidence threshold.
5. Click **Inspect Package**.
6. Review the detection boxes, item counts, package status, and processing time.

## Notes
The application requires a trained model weights file. Update the model path to match the actual location of `best.pt`.

Final evaluation metrics must be reported using actual test-set results.


import time
from pathlib import Path

import streamlit as st
from PIL import Image
from ultralytics import YOLO

from Inspection.inspector import inspect_package


st.set_page_config(
    page_title="Packaging Quality Inspection",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Industrial Packaging Quality Inspection")
st.write("Upload a package image to inspect its contents.")

weights_path = st.sidebar.text_input(
    "Trained model path",
    "model_training/runs/packaging/baseline/weights/best.pt",
)

confidence = st.sidebar.slider(
    "Confidence threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.50,
    step=0.05,
)

uploaded_file = st.file_uploader(
    "Upload package image",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    st.image(
        image,
        caption="Uploaded package",
        use_container_width=True,
    )

    if st.button("Inspect Package", type="primary"):
        if not Path(weights_path).is_file():
            st.error(
                "Model weights not found. Please check the "
                "path to your trained best.pt file."
            )
            st.stop()

        try:
            with st.spinner("Inspecting package..."):
                start_time = time.perf_counter()

                model = YOLO(weights_path)
                prediction = model.predict(
                    source=image,
                    conf=0.0,
                    verbose=False,
                )[0]

                detections = []

                if prediction.boxes is not None:
                    for box in prediction.boxes:
                        class_id = int(box.cls.item())
                        class_name = model.names[class_id]

                        detections.append({
                            "class_name": str(class_name),
                            "confidence": float(box.conf.item()),
                            "bbox": [
                                float(value)
                                for value in box.xyxy[0].tolist()
                            ],
                        })

                report = inspect_package(
                    detections,
                    confidence_threshold=confidence,
                )

                elapsed = time.perf_counter() - start_time

            st.subheader("Inspection Result")

            annotated_image = prediction.plot()
            annotated_image = annotated_image[:, :, ::-1]

            st.image(
                annotated_image,
                caption="Detected items",
                use_container_width=True,
            )

            if report["is_correct"]:
                st.success("PACKAGE CORRECT")
            else:
                st.error("PACKAGE INCORRECT")

            st.write(report["message"])

            st.subheader("Item Counts")

            st.write("Expected:", report["expected_counts"])
            st.write("Detected:", report["detected_counts"])

            if report["unexpected_items"]:
                st.warning(
                    f"Unexpected items: {report['unexpected_items']}"
                )

            st.metric(
                "Processing Time",
                f"{elapsed:.3f} seconds",
            )

            st.caption(
                "Processing time includes model loading and inference."
            )

        except Exception as error:
            st.error(f"Inspection failed: {error}")

else:
    st.info(
        "Expected package: 2 pencils, 1 eraser, and 1 ruler."
    )


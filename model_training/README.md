**1. Introduction**
This project implements an automated quality inspection system for stationery packaging using computer vision. The objective is to detect stationery items in a package and verify whether the package contains the required quantities: 2 pencils, 1 eraser, and 1 ruler. (A pencil sharpener is also detected but is optional).
The system utilizes a fine-tuned YOLO11n (You Only Look Once) object detection model to locate and classify the items, followed by a rule-based Python script to count the detected objects and render a "PACKAGE COMPLETE" or "PACKAGE NEEDS REVIEW" verdict.


**2. Dataset and Training Setup**
    •	Dataset: The Roboflow Stationery Dataset (v7).
    •	Classes (4): Eraser, Pencil, Pencil Sharpener, Ruler.
    •	Data Split:
                o	Training: 2,268 images
                o	Validation: 111 images
                o	Test: 206 images
    •	Model Architecture: yolo11n.pt (A lightweight, 2.6M parameter model ideal for fast inference).
    •	Training Environment: Google Colab (Tesla T4 GPU).
    •	Hyperparameters: 50 Epochs, Image Size: 640x640, Batch Size: 16, Optimizer: AdamW, Early Stopping Patience: 10.


**3. Training Progress**
The training process was monitored via loss and metric curves. As shown in the results.png below, the model converged well over the 50 epochs:
    •	Loss: Both training and validation box loss, classification loss, and distribution focal loss (DFL) decreased steadily, indicating the model         successfully learned the dataset features.
    •	Metrics: Precision, Recall, mAP@0.5, and mAP@0.5:0.95 all increased consistently and plateaued near the end, showing the model reached its           maximum learning capacity for this architecture.
      <img width="938" height="469" alt="image" src="https://github.com/user-attachments/assets/b751bf31-014b-491b-ba8f-f11cc22624ad" />

**4. Evaluation Results**
The model was evaluated on the unseen Test Set (206 images) to gauge real-world performance.
  **4.1 Overall Metrics**
      •	mAP@0.5 (Mean Average Precision): 0.821 (Note: The PR Curve below shows the validation score of 0.804)
      •	mAP@0.5:0.95: 0.631
      •	Precision: 0.834
      •	Recall: 0.722
  **4.2 Per-Class Performance**
The model performs exceptionally well on pencils but struggles slightly with the pencil sharpener, likely due to fewer instances in the dataset.
<img width="1354" height="384" alt="image" src="https://github.com/user-attachments/assets/3df7330a-a555-4754-8298-a311e70c609f" />


**4.3 Precision-Recall & F1 Curves**
The PR curve below demonstrates the trade-off between precision and recall. The pencil class (orange) achieves near-perfect precision at lower recall thresholds.
<img width="936" height="625" alt="image" src="https://github.com/user-attachments/assets/867c1082-43da-4787-8123-b10cba8a2b4d" />

The F1-Confidence curve shows that the optimal F1 score of 0.75 is achieved at a confidence threshold of roughly 0.505.
<img width="936" height="625" alt="image" src="https://github.com/user-attachments/assets/2f67d052-0aad-4315-852b-b83d1e582210" />

**4.4 Confusion Matrix**
The normalized confusion matrix reveals how well the model distinguishes between classes:
    •	Pencil: 100% (1.00) correctly identified (though 64% were predicted as background during specific validation batches).
    •	Eraser: 80% correctly identified.
    •	Ruler: 76% correctly identified.
    •	Pencil Sharpener: 67% correctly identified; it is sometimes confused with an eraser (13%).
    •	There is a moderate false-positive rate where background was predicted as pencil (the 0.64 column).
<img width="938" height="703" alt="image" src="https://github.com/user-attachments/assets/726bad83-88ae-47db-882d-9aa3fc5d15c5" />


**5. Inference and Package Inspection (predict.py)**
The predict.py script loads the trained best.pt weights, runs inference on an input image, counts the detected classes, and applies the packaging logic.
Example Output-
<img width="975" height="298" alt="image" src="https://github.com/user-attachments/assets/3d7632ed-2c15-452b-836e-b17a471f3790" />

<img width="781" height="781" alt="image" src="https://github.com/user-attachments/assets/1ec8f3d4-9bcb-4fba-90ac-50fe498b111c" />

**6. Limitations and Future Work**
    1.	Recall limit (0.722): The model misses roughly 28% of objects in the test set. In a packaging scenario, this manifests as false alarms where         the system says an item is missing when it is actually there.
    2.	Dataset Domain: The test images are individual stationery photos rather than photos of compiled packages. Future work should include       
        creating a dataset of actual packed kits to test the inspection logic directly.
    3.	Class Imbalance: The pencil sharpener class has fewer instances, resulting in the lowest mAP (0.759). Adding more sharpener images would 
        improve this.
    4.	Model scaling: Using a larger model (e.g., yolo11s.pt or yolo11m.pt) and training for 100+ epochs could push mAP above 0.90.



    






# Empty-label visual review — Stationery v7

## Scope and result
Reviewed the 19 empty-label images identified in empty_label_files.txt using the uploaded original stationery.v7i.yolov8.zip. Screened all 19 in a contact sheet, inspected the green measuring-tool image and the mouse image at full resolution, and compared existing annotations in two related mosaic images and a sample of 16 ruler-labeled crops.

- 18 images: no clearly visible instance of the four target classes at the reviewed resolution; retain their empty labels provisionally as background examples.
- 1 image: triangular measuring tools/set squares; retain unchanged pending a documented definition of the ruler class.
- No dataset labels or images were modified by this review.

The four classes are eraser (0), pencil (1), pencil sharpener (2), and ruler (3). An empty label can be correct when none of these classes is present.

## Important correction to earlier guidance
Visible measurement markings do not by themselves establish that an object belongs to this dataset's ruler class. The green image primarily contains triangular set squares/protractor-like tools, rather than an unambiguous straight ruler. Earlier guidance to add ruler boxes was premature.

In the two related mosaic images, the green set-square region is also unannotated; a separate straight ruler is labeled in one mosaic. A sample of ruler annotations primarily covers straight rulers. This suggests a narrower class definition, but does not prove the creator's intent because no formal class definition was supplied.

Recommended project policy: define ruler as a straight measuring ruler and explicitly document whether triangular set squares are excluded. Until that policy is confirmed, keep the green image flagged rather than create guessed boxes. If triangular tools are included, review comparable images across the dataset consistently before using their annotations as ground truth.

## Per-image screening
Numbers match review_contact_sheet.jpg. Paths below refer to label files; the matching image has the same stem in the images folder.

| No. | Label file | Observation | Decision |
| --- | --- | --- | --- |
| 1 | `test/labels/1650548802846_nmz_jpg.rf.2c7d650eb29d48c7902c034857e8e93a.txt` | Wooden surface/edge; no clear target | Background candidate; retain empty label |
| 2 | `test/labels/20220402_231341_atm_jpg.rf.805eb661a8de1013c7e48166d5f7c695.txt` | Wooden drawers and handles | Background candidate; retain empty label |
| 3 | `test/labels/20220419_200034_atm_jpg.rf.505e17d2248eb8499d15be1bad53c048.txt` | Blurred outdoor scene | Background candidate; retain empty label |
| 4 | `test/labels/20220419_201103_atm_jpg.rf.e1593bbbd7b2f43189304a45a4b8e5c9.txt` | Outdoor wall and bench | Background candidate; retain empty label |
| 5 | `test/labels/IMG_20220411_111123_nmz_jpg.rf.de9efe524030a079e2cee503d63e92ab.txt` | Plain brown surface | Background candidate; retain empty label |
| 6 | `train/labels/20220331_172958_atm_jpg.rf.bdded9f80596239121892fa964f65b8f.txt` | Overlapping green triangular measuring tools | Class-definition review; preserve unchanged |
| 7 | `train/labels/20220401_140603_atm_jpg.rf.d7ea09a06663c51a9adea6e01312b2f3.txt` | Outdoor ground and metal/stone fragment | Background candidate; retain empty label |
| 8 | `train/labels/20220419_184251b_jpg.rf.a10c8b6689b10e5eff07ca46555b0f00.txt` | Outdoor tree and building | Background candidate; retain empty label |
| 9 | `train/labels/20220419_184419b_jpg.rf.3c2ac294f40c2bc024cba626582ac3a3.txt` | Outdoor building | Background candidate; retain empty label |
| 10 | `train/labels/20220419_185108b_jpg.rf.d1fedc83b047ad93958f499c3eac9f91.txt` | Outdoor building and vegetation | Background candidate; retain empty label |
| 11 | `train/labels/IMG_20220410_143356_nmz_jpg.rf.649d56c90cdcdd7feccd5be3c5479519.txt` | Drink bottle on ground | Background candidate; retain empty label |
| 12 | `train/labels/IMG_20220410_144736_nmz_jpg.rf.ed628580d4beef9e03d66e8e338de895.txt` | Plain textured surface | Background candidate; retain empty label |
| 13 | `train/labels/IMG_20220410_212906_nmz_jpg.rf.3f5e6c3bc2f7c264f2e57b8a84a49540.txt` | Night street scene | Background candidate; retain empty label |
| 14 | `train/labels/IMG_20220410_213812_nmz_jpg.rf.7baa7e6ed9d2095789a66f35484be7c7.txt` | Blue-lit building/wall | Background candidate; retain empty label |
| 15 | `train/labels/IMG_20220410_223855_nmz_jpg.rf.72ef2650ec4439f0b5e29ab6e20b868e.txt` | Close-up textured surface | Background candidate; retain empty label |
| 16 | `train/labels/IMG_20220410_234439_nmz_jpg.rf.d4eb886f812ee01ed9427d397a6a3457.txt` | Wooden and dark surfaces | Background candidate; retain empty label |
| 17 | `train/labels/IMG_20220411_110635_nmz_jpg.rf.ee87b3bf8ebe6e63bce844b177b421ad.txt` | Patterned fabric | Background candidate; retain empty label |
| 18 | `train/labels/IMG_20220411_110806_nmz_jpg.rf.db3d91a09cb9770c511015c81abca5e0.txt` | Computer mouse on patterned fabric | Background candidate; retain empty label |
| 19 | `valid/labels/1650548685907_nmz_jpg.rf.14a5649de2204e14b51586081a130243.txt` | Textured surface | Background candidate; retain empty label |

## Limits and next steps
This is an assistant-produced visual screening, not an independent annotation benchmark. Very small, blurred, occluded, or ambiguous instances can be missed. The 18 background decisions are provisional visual judgments. The contact sheet and source paths are provided so the team can review them.

This review does not establish that nonempty labels are accurate or complete, that the train/validation/test sets are independent, or that the model will meet a performance target. Similar and mosaic image overlap needs a separate audit.

Do not delete all empty label files merely because they are empty. Do not rename unrelated images to match existing labels. The extra collage file ending in "(2).jpg" seen in the user's screenshot is not part of the reviewed original ZIP; inspect and move accidental additions outside the training folders before rerunning the dataset checker.

## Reproducibility and credit
Source: https://universe.roboflow.com/lalaworkspace/stationery-l7qrn/dataset/7
Dataset creator: Lalaworkspace. Dataset license: CC BY 4.0.
The contact sheet is a resized arrangement of the creator's images with review numbers added. Image content was not generated. This review and contact sheet are derived from the uploaded original export; they do not include local label edits or later-added files.

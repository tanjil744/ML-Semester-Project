"""Preview or apply four reviewed Stationery v7 source-group corrections.

Python standard library only. Default: print a plan and change nothing.
With --apply: create a NEW dataset copy, move images with their labels,
update the new copy's data.yaml paths, and record the changes.

Scope: the 14 reviewed family members from pairs 1, 2, 4, and 8.
This does not establish independence of every source or mosaic component.
Dataset credit: Stationery v7 by Lalaworkspace, CC BY 4.0.
"""

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SPLITS = ("train", "valid", "test")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
GROUPS = [{'pair': 1,
  'family_keys': ['292', '171'],
  'target_split': 'train',
  'members': [{'path': 'test/images/171_jpg.rf.bb195a6f4797b5e12a6e2f0d1e31ec54.jpg',
               'sha256': '2d1220bc5ad6e20d51d9fa120f5821adeccaeea2a9dd01eaf4ffa8e8f99e6869'},
              {'path': 'train/images/292_jpg.rf.a9b80f6ee01440aa1db3f7580e8aba2c.jpg',
               'sha256': '67f852106a239e5ce219ae83e85934b44e514724d0de8cba4fad10530ccaeada'},
              {'path': 'train/images/292_jpg.rf.cbed058602512a8ed52860cecffa702f.jpg',
               'sha256': '3c13ccef2fff6bb732451eec107a0a9946536a350ff6507e31e4c933e30a6b7e'},
              {'path': 'train/images/292_jpg.rf.faf51b390f1271d6538dd749b1c221fd.jpg',
               'sha256': '9158edf53638a5b35d6032845fee070a6a998901ec3b262c4a7b6d2aef4681f7'}]},
 {'pair': 2,
  'family_keys': ['378977_1'],
  'target_split': 'train',
  'members': [{'path': 'train/images/378977_1.rf.26e737bc00500f73f36ddfc460814d50.jpg',
               'sha256': '4b150a1caa83c6aa54a7edcd973c382ebc230e6a947f3df6d013cc5d6d27d787'},
              {'path': 'train/images/378977_1.rf.916456fbf80176d5fe633a6a00927935.jpg',
               'sha256': '665041580b1c1d3a5ee3f719638eb459ff068c40348cc68533318ecad4c91a11'},
              {'path': 'train/images/378977_1.rf.f688e98e06c91622d6ef786dce33bc5a.jpg',
               'sha256': 'db8197d2c20cdf36121aa12815f11e52fd267a3f7ab069e6fe10ef4d325e813a'},
              {'path': 'valid/images/378977_1_jpg.rf.fff928a7f5ed3c60a0ca4e49ab844496.jpg',
               'sha256': '7339fbd6a9aa1f1dd4b427ceb4dea72b4d4d2ef1228e93bf6b9b4a3a398f6bea'}]},
 {'pair': 4,
  'family_keys': ['83'],
  'target_split': 'valid',
  'members': [{'path': 'test/images/83_jpg.rf.5dd73a08f5803619652c6511b52f3c04.jpg',
               'sha256': '52cec09271087f73ee08ed9d4879ec688f424bb7c231b4bc9f935e4d941ed32e'},
              {'path': 'valid/images/83.rf.cb0969d9a243b31a5845c49a6cf8f39c.jpg',
               'sha256': '26cbad01d4a6f751511e7d724a2a5552f4036cd5702e35eb55d045c94a338507'}]},
 {'pair': 8,
  'family_keys': ['73', '92'],
  'target_split': 'train',
  'members': [{'path': 'test/images/92_jpg.rf.41293faead90c286efdfe5f6ffdcc935.jpg',
               'sha256': 'a108dd209681fa45a57a000432478ff39e92ff52d0d8c938e4dd35239a44efa7'},
              {'path': 'train/images/73_jpg.rf.2d47bb988a03a57ee003c3ac323b9c31.jpg',
               'sha256': '23746405871323d9e8c5f59d85468bfbf37fc297b439de6e72365ea27d4414e1'},
              {'path': 'train/images/73_jpg.rf.416de1b3584310429fcdae8e19372f06.jpg',
               'sha256': '93b149accfbf0fb07be2b33ffdf6092c8b669e34f7abb143cf3cde49972f8873'},
              {'path': 'train/images/73_jpg.rf.d1437d9b4238521ac3ef30c0140ec8ae.jpg',
               'sha256': '063dddaf2e4a1d42cf295e7e80852dd21ea4ba8e3f1d02c7afaae4aa5bdcfef5'}]}]


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def family_key(path):
    prefix = path.name.split(".rf.")[0]
    return re.sub(r"(?:_jpg|_png|\.jpg|\.png)$", "", prefix, flags=re.I)


def inventory(root):
    counts = {}
    for split in SPLITS:
        image_dir = root / split / "images"
        label_dir = root / split / "labels"
        if not image_dir.is_dir() or not label_dir.is_dir():
            raise ValueError(f"Missing images/labels directory for {split}.")
        images = [p for p in image_dir.iterdir()
                  if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        labels = list(label_dir.glob("*.txt"))
        if len({p.stem for p in images}) != len(images):
            raise ValueError(f"Multiple image files share a stem in {split}.")
        if {p.stem for p in images} != {p.stem for p in labels}:
            raise ValueError(f"Image-label pairing mismatch in {split}.")
        counts[split] = {"images": len(images), "labels": len(labels)}
    return counts


def make_plan(root):
    before = inventory(root)
    if not (root / "data.yaml").is_file():
        raise ValueError("Missing data.yaml in the dataset folder.")
    plan = []
    for group in GROUPS:
        known = {member["path"] for member in group["members"]}
        discovered = {
            p.relative_to(root).as_posix()
            for split in SPLITS
            for p in (root / split / "images").iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
            and family_key(p) in group["family_keys"]
        }
        if discovered != known:
            raise ValueError(
                f"Pair {group['pair']}: family membership differs from the reviewed export. "
                f"Missing: {sorted(known - discovered)}; "
                f"unreviewed members: {sorted(discovered - known)}."
            )
        for member in group["members"]:
            image = root / member["path"]
            if digest(image) != member["sha256"]:
                raise ValueError(f"Image content differs from reviewed source: {image.name}")
            source_label = Path(member["path"].replace("/images/", "/labels/")).with_suffix(".txt")
            if not (root / source_label).is_file():
                raise ValueError(f"Missing label: {source_label}")
            source_split = Path(member["path"]).parts[0]
            if source_split == group["target_split"]:
                continue
            dest_image = Path(group["target_split"]) / "images" / image.name
            dest_label = Path(group["target_split"]) / "labels" / source_label.name
            if (root / dest_image).exists() or (root / dest_label).exists():
                raise ValueError(f"Destination filename collision: {image.name}")
            plan.append({
                "pair": group["pair"],
                "image_from": member["path"], "image_to": dest_image.as_posix(),
                "label_from": source_label.as_posix(), "label_to": dest_label.as_posix(),
                "image_sha256": member["sha256"],
                "label_sha256": digest(root / source_label),
            })
    return before, plan


def update_yaml(path, final_root):
    # Preserve class names, attribution, license, and other source metadata.
    replacements = {
        "path": "'" + final_root.as_posix().replace("'", "''") + "'",
        "train": "train/images", "val": "valid/images", "test": "test/images",
    }
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    seen = set()
    for index, line in enumerate(lines):
        key = line.split(":", 1)[0]
        if key in replacements:
            if key in seen:
                raise ValueError(f"Duplicate top-level YAML field: {key}")
            seen.add(key)
            lines[index] = f"{key}: {replacements[key]}"
    missing = [f"{key}: {value}" for key, value in replacements.items() if key not in seen]
    path.write_text("\n".join(missing + lines) + "\n", encoding="utf-8")


def apply_plan(source, destination, before, plan):
    if destination.exists():
        raise ValueError(f"Output already exists; nothing overwritten: {destination}")
    if destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError("Source and output must be separate, non-nested folders.")
    if not destination.parent.is_dir():
        raise ValueError("The output parent directory does not exist.")
    with tempfile.TemporaryDirectory(prefix="split_review_build_", dir=destination.parent) as tmp:
        copied = Path(tmp) / "dataset"
        shutil.copytree(source, copied)
        # Verify reviewed image/label contents before any moves in the new copy.
        for change in plan:
            for kind in ("image", "label"):
                if digest(copied / change[f"{kind}_from"]) != change[f"{kind}_sha256"]:
                    raise ValueError("Source changed while copying; no final output created.")
        for change in plan:
            for kind in ("image", "label"):
                shutil.move(str(copied / change[f"{kind}_from"]),
                            str(copied / change[f"{kind}_to"]))
        after = inventory(copied)
        if sum(v["images"] for v in before.values()) != sum(v["images"] for v in after.values()):
            raise ValueError("Unexpected change in total image count.")
        for group in GROUPS:
            for member in group["members"]:
                expected = copied / group["target_split"] / "images" / Path(member["path"]).name
                if not expected.is_file() or digest(expected) != member["sha256"]:
                    raise ValueError("Reviewed group verification failed.")
        original_yaml = (copied / "data.yaml").read_text(encoding="utf-8-sig")
        update_yaml(copied / "data.yaml", destination)
        report = {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "source": str(source), "output": str(destination),
            "before": before, "after": after,
            "policy": "Keep reviewed families already in train within train; otherwise keep in valid.",
            "groups": GROUPS, "moves": plan, "source_data_yaml": original_yaml,
            "label_content_changes": 0,
            "limitations": [
                "Only the four reviewed source families are handled.",
                "Other perceptual candidates and mosaic component provenance still require review.",
                "This is not proof of complete split independence or model performance.",
            ],
            "credit": "Stationery v7 by Lalaworkspace, CC BY 4.0.",
        }
        (copied / "split_corrections.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if destination.exists():
            raise ValueError("Output appeared during copying; refusing to overwrite.")
        copied.rename(destination)
    return after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--apply", action="store_true", help="Create a new corrected copy after showing the plan.")
    parser.add_argument("--output", type=Path, help="New output directory; must not already exist.")
    args = parser.parse_args()
    source = args.dataset.resolve()
    destination = (args.output or source.with_name(source.name + "_reviewed_splits")).resolve()
    try:
        before, plan = make_plan(source)
        print("Reviewed source groups: 4 (14 known images, including training mosaics)")
        print(f"Planned image-label pair moves: {len(plan)}")
        for change in plan:
            print(f"  Pair {change['pair']}: {change['image_from']} -> {change['image_to']}")
        if not args.apply:
            print("\nPREVIEW ONLY: no files changed and no output directory created.")
            print(f"New copy with --apply: {destination}")
        else:
            after = apply_plan(source, destination, before, plan)
            print(f"\nNew dataset copy created: {destination}")
            for split, values in after.items():
                print(f"{split}: {values['images']} images, {values['labels']} labels")
            print("Label contents preserved. Change log: split_corrections.json")
            print("Next: run the format/pairing checker on the NEW copy.")
        print("Scope: four reviewed families only; wider overlap review remains pending.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Stopped: {error}\n")


if __name__ == "__main__":
    main()

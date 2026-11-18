"""Reconstruct the reviewed dataset from raw sources and final annotations."""

import argparse
import csv
import io
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIELDS = ["id", "text", "label", "split"]


def prepare(output):
    texts = {}
    with ZipFile(DATA / "raw/06_sc_train_ib.zip") as archive:
        with archive.open("06_sc_train_ib.csv") as member:
            for row in csv.DictReader(io.TextIOWrapper(member, encoding="utf-8-sig")):
                texts[row["custom_id"]] = row["text"].strip()
    with (DATA / "shared.csv").open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            texts[row["kazsandra_id"]] = row["text"].strip()
    with (DATA / "final_annotations.csv").open(encoding="utf-8-sig", newline="") as file:
        annotations = list(csv.DictReader(file))
    if len(annotations) != 5000 or len({row["id"] for row in annotations}) != 5000:
        raise ValueError("Expected 5,000 unique annotation records")
    rows = []
    for annotation in annotations:
        source_id = annotation["id"]
        if source_id not in texts:
            raise ValueError(f"Missing source text for {source_id}")
        if annotation["label"] not in ("0", "1") or annotation["split"] not in ("train", "val", "test"):
            raise ValueError(f"Invalid annotation for {source_id}")
        text = annotation["text_override"] or texts[source_id]
        if not text.strip():
            raise ValueError(f"Empty review for {source_id}")
        rows.append({"id": source_id, "text": text,
                     "label": annotation["label"], "split": annotation["split"]})
    if output.resolve() in {path.resolve() for path in (
        DATA / "shared.csv", DATA / "final_annotations.csv", DATA / "raw/06_sc_train_ib.zip"
    )}:
        raise ValueError("Output must differ from source inputs")
    with output.open("x", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Prepared {len(rows)} reviews in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DATA / "kazakh_profanity.csv")
    prepare(parser.parse_args().output)

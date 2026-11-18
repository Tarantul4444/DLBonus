"""Assign grouped reviews to balanced 80/10/10 splits, preserving labels."""

import csv
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


PATH = Path(__file__).resolve().parent.parent / "data/kazakh_profanity.csv"
SEED = 42
SIMILARITY = 0.88
SPLITS = ("train", "val", "test")
RATIOS = np.array([0.8, 0.1, 0.1])


def main():
    original = PATH.read_bytes()
    with PATH.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        rows = list(reader)
    if fields != ["id", "text", "label", "split"] or len(rows) != 5000:
        raise ValueError("Expected the four-column, 5,000-review dataset")
    texts = [" ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", row["text"]).casefold()))
             for row in rows]
    parent = list(range(len(rows)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(a, b):
        parent[find(b)] = find(a)

    signatures = {}
    for index, text in enumerate(texts):
        # Collapse repeated words to group short repeated curses.
        signature = re.sub(r"\b(\w+)(?:\s+\1\b)+", r"\1", text)
        if signature in signatures:
            union(index, signatures[signature])
        signatures[signature] = index

    matrix = TfidfVectorizer(analyzer="char", ngram_range=(3, 5)).fit_transform(texts)
    for start in range(0, len(rows), 250):
        similarities = (matrix[start:start + 250] @ matrix.T).tocoo()
        for offset, other, score in zip(similarities.row, similarities.col, similarities.data):
            index = start + offset
            if index < other and score >= SIMILARITY:
                union(index, other)

    groups = defaultdict(list)
    for index in range(len(rows)):
        groups[find(index)].append(index)
    strata = sorted({(row["label"], row["id"][:3]) for row in rows})
    stratum_index = {value: index for index, value in enumerate(strata)}
    totals = Counter((row["label"], row["id"][:3]) for row in rows)
    targets = RATIOS[:, None] * np.array([totals[value] for value in strata])[None, :]
    group_vectors = {}
    for group, members in groups.items():
        vector = np.zeros(len(strata))
        for index in members:
            row = rows[index]
            vector[stratum_index[row["label"], row["id"][:3]]] += 1
        group_vectors[group] = vector

    rng = random.Random(SEED)
    ordered = list(groups)
    rng.shuffle(ordered)
    ordered.sort(key=lambda group: len(groups[group]), reverse=True)
    assigned = np.zeros_like(targets)
    capacities = np.array([4000, 500, 500])
    group_splits = {}
    for group in ordered:
        vector = group_vectors[group]
        size = len(groups[group])
        choices = []
        for split_index in range(3):
            if assigned[split_index].sum() + size > capacities[split_index]:
                continue
            before = assigned[split_index] - targets[split_index]
            after = before + vector
            delta = np.sum((after ** 2 - before ** 2) / np.maximum(targets[split_index], 1))
            choices.append((delta, split_index))
        if not choices:
            raise ValueError("Could not place a review group within split capacities")
        _, split_index = min(choices)
        assigned[split_index] += vector
        group_splits[group] = SPLITS[split_index]

    for index, row in enumerate(rows):
        row["split"] = group_splits[find(index)]
    assert Counter(row["split"] for row in rows) == dict(zip(SPLITS, capacities))
    assert all(len({rows[index]["split"] for index in members}) == 1 for members in groups.values())
    assert PATH.read_bytes() == original, "Dataset changed during resplitting"
    temporary = PATH.with_suffix(".split.tmp")
    with temporary.open("x", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with temporary.open(encoding="utf-8-sig", newline="") as file:
        assert list(csv.DictReader(file)) == rows
    temporary.replace(PATH)
    print("Class counts:", sorted(Counter((row["split"], row["label"]) for row in rows).items()))
    print("Source counts:", sorted(Counter((row["split"], row["id"][:3]) for row in rows).items()))
    print("Groups:", len(groups), "with multiple reviews:", sum(len(g) > 1 for g in groups.values()))
    print("Groups with conflicting labels:", sum(len({rows[i]["label"] for i in g}) > 1 for g in groups.values()))


if __name__ == "__main__":
    main()

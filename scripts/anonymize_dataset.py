"""Redact recognizable personal identifiers from the project CSV."""

import csv
import hashlib
import re
from collections import Counter
from io import BytesIO, TextIOWrapper
from pathlib import Path


PATH = Path(__file__).resolve().parent.parent / "data/kazakh_profanity.csv"
PATTERNS = [
    ("EMAIL", re.compile(r"(?<!\w)[\w.+-]+@[\w.-]+\.[a-z]{2,}", re.I)),
    ("URL", re.compile(r"(?:https?://|www\.)[^\s<>]+", re.I)),
    ("HANDLE", re.compile(r"(?<![\w@])@[A-Za-z][A-Za-z0-9_.]{2,}\b")),
    ("PHONE", re.compile(r"(?<!\w)(?:\+7|8)[\s().-]*(?:\d[\s().-]*){9}\d(?!\w)")),
    ("IDENTIFIER", re.compile(r"(?<!\w)\d{12}(?!\w)")),
]

# Contextual replacements cover introductions and disclosures found during review.
# Profane pseudonyms such as «Менің атым қотақбас» retain their task-relevant text.
REVIEWED_HASHES = {'pla061300pla': {'2d01810fafe81b1895bbfd26a71b8cab83d5a0bc4ca09eaca57baa45a368b406': '[PERSON]', '9ed95b57b07a6f2f4ce607b289bac9d1528f80638a10e73e88365ee5810458ef': '[PERSON]', '10f82f24e515011924d7e251f24519b4a5f71ed4777f7c644f4527ebe22f8506': '[PERSON]', 'ddaa9924ee05c2e3eb4f4fb465aabe0858426a20c0835780966a9d65e9fef291': '[PERSON]', '4cdd67555c80a7b4af912f6ceb6db915bd5c3ba2da4be00250a9f0867fc195e0': '[PERSON]', 'c3ceee81547c976ebe6a0c0e3baceda6f41374b42195b09ee58a1da5f67e0847': '[PERSON]', 'e07e88dcd50dd4c120f2198d58f3af5419c7a199a1ba891ecc9fe9f719261822': '[PERSON]', '946abf9ba1ae3b2b01eeb493ae71c10acbcf179d2fdab0506ab1b050fd1c85f1': '[PERSON]'}, 'pla069623pla': {'5772eb88d2f1b8e8af2979bec6afb4136703b0dbee64d28f689f8c16efb64fd0': '[PERSON]'}, 'pla060184pla': {'c0a431327ee4f5336c95b4dec14883b3d8a6cf9ecc818ff4d5245f97d105e73f': '[PERSON]'}, 'pla077223pla': {'fadf71d75aca55b4bbf9f01eadb2c7cc15ed19ad511a093c62559c86c1426e9e': '[PERSON]'}, 'pla051153pla': {'9cff730a56095fdd2de0c8a94c629973c07709ef40fe8fb388ee5ea69758d680': '[SCHOOL]', 'c638b507bd7755019fb43890100e53d7217a476f01c2311a15059f85829812aa': '[GRADE]', '098a36707bc43aaf0c12c66c8d29803b8eacfcd7b5a3af1ed893058ce257e2e2': '[PERSON]', 'a1505d4f41eca805f47e0b454dd0e951fe31a938896b9e0841256d5711e8f7b4': 'Жасым [AGE]'}}


def redact(row, counts):
    text = row["text"]
    for kind, pattern in PATTERNS:
        text, count = pattern.subn(f"[{kind}]", text)
        counts[kind] += count
    # Match reviewed spans by hash so the script does not contain personal data.
    replacements = REVIEWED_HASHES.get(row["id"], {})
    words = list(re.finditer(r"\w+(?:-\w+)*", text))
    spans = []
    for index, match in enumerate(words):
        for length in (1, 2, 3):
            if index + length > len(words):
                continue
            end = words[index + length - 1].end()
            candidate = text[match.start():end]
            digest = hashlib.sha256(candidate.casefold().encode()).hexdigest()
            if digest in replacements:
                replacement = replacements[digest]
                spans.append((match.start(), end, replacement))
    for start, end, replacement in sorted(spans, reverse=True):
        text = text[:start] + replacement + text[end:]
        counts[replacement] += 1
    return {**row, "text": text}


def main():
    original = PATH.read_bytes()
    with TextIOWrapper(BytesIO(original), encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        rows = list(reader)
    counts = Counter()
    updated = [redact(row, counts) for row in rows]
    assert len(updated) == len(rows)
    assert all(all(before[key] == after[key] for key in ("id", "label", "split"))
               for before, after in zip(rows, updated))
    if updated != rows:
        temporary = PATH.with_suffix(".redact.tmp")
        with temporary.open("x", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(updated)
        with temporary.open(encoding="utf-8-sig", newline="") as file:
            assert list(csv.DictReader(file)) == updated
        assert PATH.read_bytes() == original, "Dataset changed during anonymization"
        temporary.replace(PATH)
    print("Changed reviews:", sum(before != after for before, after in zip(rows, updated)))
    print("Replacements:", dict(counts))


if __name__ == "__main__":
    main()

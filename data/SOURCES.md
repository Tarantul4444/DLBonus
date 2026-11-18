# Dataset sources

The working dataset is `kazakh_profanity.csv`. It contains 5,000 real reviews with revised labels and grouped train/validation/test splits.

## Shared annotation

The original input was `kazakh_profanity_share.xlsx`, assembled collaboratively. It contained 3,061 rows with columns `kazsandra_id`, `text`, `label`, and `split`. The initial build retained 3,020 rows after filtering contacts and duplicates. Labels and splits were subsequently revised.

The source workbook has been exported faithfully to `shared.csv` with 3,061 rows and its original columns, labels, and splits. The export is a local raw input and is ignored by Git because it has not been anonymized. Use this local source export for reconstruction.

## KazSAnDRA

- Authors: Rustem Yeshpanov and Huseyin Atakan Varol.
- Repository: https://github.com/IS2AI/KazSAnDRA
- Paper: https://aclanthology.org/2024.lrec-main.844/
- Download: https://raw.githubusercontent.com/IS2AI/KazSAnDRA/main/dataset/06_sc_train_ib.zip
- Local archive: `raw/06_sc_train_ib.zip`.
- License: CC BY 4.0, as described by the dataset authors.
- Archive member: `06_sc_train_ib.csv`.

The initial build added 1,980 reviews from the Market and Appstore domains. Original numeric ratings describe sentiment and were not used as profanity labels. The initial class labels used keyword rules, followed by contextual review and corrections.

The raw archive is retained locally and ignored by Git. Repository users can download it from the link above. Raw source texts have not been anonymized by our working-dataset redaction script.

## Annotation reference

https://huggingface.co/datasets/Rustem-Kaimolla/kazakh-swear-words was consulted as a vocabulary reference. Its records were not merged into the current real-review dataset. Earlier synthetic draft files were removed.

See `kazakh-only-labeling.md` for the current annotation rules and limitations. The initial XLSX was assembled collaboratively. I individually added real KazSAnDRA reviews with manual work and AI assistance. Preliminary labels were produced with AI assistance and manual corrections, and I personally reviewed all 5,000 records afterwards

## Final reviewed decisions

`final_annotations.csv` stores the selected review IDs, final labels, split assignments, and text overrides. Together with the two raw inputs, it reproduces the authoritative four-column CSV through `scripts/prepare_dataset.py`. The output has been checked for byte-for-byte equality.

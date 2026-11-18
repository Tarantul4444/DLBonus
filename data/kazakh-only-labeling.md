# Kazakh profanity annotation policy

The authoritative dataset is `kazakh_profanity.csv`. It contains 5,000 real reviews with columns `id`, `text`, `label`, and `split`.

## Labels

- Class 1 indicates recognizable Kazakh profanity, including inflections, transliteration, misspellings, and recoverable masking. Mixed-language reviews need at least one target Kazakh expression.
- Class 0 includes Russian profanity alone, ordinary negative reviews, and topical mentions such as pornography or sex without a target expression.
- Under the current project policy, insulting uses of Kazakh livestock terms such as mal and variants such as malski receive 1. Literal livestock references receive 0. This extends the boundary beyond a strict obscene-word definition.
- Recognizable shortened curses involving sheshenning or shesheng receive 1 when their context supports that reading. Literal family references, rhetoric, and geographic names receive 0 without another target expression.
- Standalone shshs variants and the numeric marker 667 receive 1. Matching substrings in longer words or numbers do not trigger this rule. The interpretation of 667 is a project-specific convention.
- Abusive expressions such as kotti kys, kotek, and standalone or abusive koten receive 1. Neutral anatomical mentions in diaper reviews remain 0 without other target expressions.
- Abusive jalep, zhalep, jalap, and their Cyrillic variants receive 1.
- Am, amshyk, and related forms require contextual interpretation. English I am, time-format AM, names, and unrelated word substrings do not trigger 1.
- Entirely masked text with no recoverable meaning is ambiguous. I resolved ambiguous cases during the final manual review according to the adopted policy.

See the English project README for Cyrillic examples and the exact current boundary.

## Process and limitations

The initial builder retained 3,020 rows from a collaboratively assembled 3,061-row XLSX collection. I individually added 1,980 real KazSAnDRA reviews using manual work and AI assistance. AI-assisted labeling and contextual corrections were followed by my complete manual review of all 5,000 records, after AI-assisted labeling.

Targeted passes covered masking, transliteration, shortened curses, insulting mal, forms of kot, jalep, and am. Some reviewed decisions are stored in `scripts/reviewed_mal_positive_ids.txt` and ID overrides in `scripts/relabel_kazakh_only.py`. Other user edits may only exist in the authoritative CSV. A rule-based rebuild is an intermediate reconstruction and may differ from the final reviewed labels.

## Current split

| Split | Class 0 | Class 1 | Total |
| --- | ---: | ---: | ---: |
| Train | 2,836 | 1,164 | 4,000 |
| Validation | 356 | 144 | 500 |
| Test | 355 | 145 | 500 |
| Total | 3,547 | 1,453 | 5,000 |

`scripts/resplit_dataset.py` uses seed 42 and targets 80/10/10 while balancing label and source-ID prefix jointly. Normalized repeated-word signatures and character 3-5-gram TF-IDF similarity of at least 0.88 link reviews into groups. Connected groups stay together. There are 12 multi-review groups, including three groups whose labels differed in the automated audit before my final review. I subsequently reviewed all records. Semantic paraphrases can escape this heuristic.

## Personal information and access

`scripts/anonymize_dataset.py` redacts detected contacts and reviewed personal disclosures. Five reviews had names or a child's school, grade, and age replaced by placeholders. Automatic detection is incomplete. Raw local inputs `shared.csv` and `raw/06_sc_train_ib.zip` have not undergone working-dataset redaction and are ignored by Git.

See `SOURCES.md` and the project `README.md` for source access, attribution, commands, and submission status. Train directly from the authoritative CSV. The preparation scripts produce intermediate files. Retrain after changing labels or splits.



## Exact reconstruction

Run `python scripts/prepare_dataset.py --output data/reconstructed.csv` from the project directory. The script uses `shared.csv`, the raw KazSAnDRA ZIP, and `final_annotations.csv`. The annotation snapshot stores all 5,000 final labels and splits in output order, plus 33 text overrides. Reconstruction was verified byte for byte against the working CSV. Historical keyword scripts and the TXT list are not required for this operation. Future manual changes must also be transferred to the annotation snapshot.

## Revised test annotations

I edited reference labels after inspecting the first final-test predictions. The final annotation snapshot has been synchronized with the working CSV. Subsequent metrics must be identified as evaluation against revised reference labels. Reconstruction reproduces the same records and row order; editor-specific CSV formatting may differ.

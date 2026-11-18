# Kazakh Profanity Detection

The model reads one Kazakh or Kazakh–Russian product review or comment and returns a binary label and a score for class 1. Class `0` means that no target Kazakh profanity was identified. Class `1` means that a target Kazakh profane expression is present under the annotation policy below. Russian profanity alone receives `0`.

## Quick start

Read [QUICK START.md](QUICK%20START.md) for the required files and notebook cells to predict your own sentence.

## Project status

The repository contains a 5,000-review dataset, grouped 80/10/10 splits, preparation scripts, and a runnable fine-tuning and prediction notebook. The current annotation policy also includes some insulting uses of Kazakh words such as `мал`. This broad boundary must be described when presenting the project.

The current trained checkpoint is in `artifacts/kaz-roberta-reviewed`. Training, validation, test evaluation, and error analysis have been completed. Test F1 is 0.9267 against the revised reference labels. Three test labels were corrected after inspecting the first evaluation, as documented below. The checkpoint is configured for distribution through Git LFS. The repository and checkpoint are distributed at https://github.com/Tarantul4444/DLBonus using Git LFS.

## 1. Prepare the dataset

### Sources and relevance

- The starting collection was assembled collaboratively in `kazakh_profanity_share.xlsx`. Its faithful CSV export is `data/shared.csv`, containing 3,061 rows with the original labels and splits. The initial builder retained 3,020 rows after filtering duplicates and obvious contact information.
- I individually expanded the collection with 1,980 real reviews from the Market and Appstore domains of KazSAnDRA, using manual selection and AI-assisted candidate retrieval. Market reviews directly concern goods. Appstore reviews concern software products and include informal complaints, spelling variation, and mixed-language text. The shared subset also contains book and location/service reviews, so the final collection has a broader domain than physical goods.
- All 5,000 examples in the working CSV are real source texts. Synthetic drafts created during exploration were discarded and are excluded from this dataset.

KazSAnDRA was released by Rustem Yeshpanov and Huseyin Atakan Varol under CC BY 4.0. Its star-rating/sentiment labels were not treated as profanity labels. The original archive used here is `06_sc_train_ib.zip`, with member `06_sc_train_ib.csv`. See [the repository](https://github.com/IS2AI/KazSAnDRA), [the paper](https://aclanthology.org/2024.lrec-main.844/), and [the archive download](https://raw.githubusercontent.com/IS2AI/KazSAnDRA/main/dataset/06_sc_train_ib.zip).

The small [Kazakh Swear Words dataset](https://huggingface.co/datasets/Rustem-Kaimolla/kazakh-swear-words) was consulted as a vocabulary reference. Its rows were not merged into the final collection.

### Annotation policy

Annotation combined AI-assisted preliminary labeling with manual contextual review. After the AI labeling and targeted corrections, I personally reviewed all 5,000 records again and confirmed or corrected their labels.

- Assign `1` for recognizable Kazakh profanity, including inflections, Latin transliteration, spelling variants, and recoverable masking.
- In mixed-language comments, assign `1` when at least one target Kazakh expression occurs. Russian profanity alone remains `0`, and the Russian text stays in the input.
- Assign `0` to negative sentiment without target profanity and topical mentions of `порно` or `секс` without a target expression.
- Recognizable shortened curses such as contextually profane `шешеннің` and standalone `щщс` or `667` receive `1`. The numeric marker is a project-specific convention and can be ambiguous in other contexts.
- The current policy assigns `1` to insulting `мал` and variants such as `малски`, and to abusive or standalone `котен`/`көтен`. Literal livestock references and neutral anatomical references receive `0`.
- Read ambiguous short forms such as `ам` in context. English `I am`, time-format `AM`, names, and unrelated word substrings remain `0` without another target expression. Unresolved ambiguous cases have provisionally retained `0` and need review.

| Text | Label | Reason |
| --- | ---: | --- |
| Сапасы нашар, ақшам босқа кетті. | 0 | Negative review without target profanity |
| Кымбаттап кетипти говно | 0 | Russian profanity alone |
| Мына ойында порно бар | 0 | A topical content reference |
| Мына ойын боқ екен | 1 | Kazakh obscene expression |
| Маған еөшірімейдіғо қ*ақбас | 1 | Recoverable masking |
| Мал шаруашылығы | 0 | Literal livestock reference |
| Тупой мал барды жоккып | 1 | Insulting use under the current policy |

See `data/kazakh-only-labeling.md` for the detailed policy and known limitations.

### Splits and leakage prevention

| Split | Class 0 | Class 1 | Total |
| --- | ---: | ---: | ---: |
| Train | 2,836 | 1,164 | 4,000 |
| Validation | 356 | 144 | 500 |
| Test | 352 | 148 | 500 |
| Total | 3,544 | 1,456 | 5,000 |

The CSV stores `id`, `text`, `label`, and `split`. Seed `42` controls selection and splitting. Exact IDs and normalized-text duplicates were filtered during preparation. The splitter groups normalized repeated-word signatures and pairs with character TF-IDF cosine similarity at least `0.88` using character 3–5-grams. Connected pairs form one group. All 12 multi-review groups are placed wholly in one split. Allocation targets 80/10/10 while balancing class and source-ID prefix jointly. Prefixes are a proxy for source, rather than independently verified domain annotations for every row.

The TF-IDF used by the splitter is only a duplicate-detection tool and is not a classifier input or learned inference preprocessing. The classifier uses a fixed pretrained tokenizer. Model and threshold selection use validation only. Semantic paraphrases can escape the duplicate heuristic. The automated audit found differing labels in three similarity groups before my final review. I subsequently reviewed all records; the grouping audit has not been repeated against a separately recorded review log.

### Personal information

`scripts/anonymize_dataset.py` replaces detected contact patterns and reviewed disclosures with placeholders. Names and a child's school, grade, and age were redacted in five working reviews. The automatic pass can miss implicit personal information. Raw `shared.csv` and the source ZIP are local source inputs and are ignored by Git because they have not undergone the working dataset's redaction process. Keep credentials out of the repository.

### Reproduce preparation

The final dataset is reconstructed from three inputs:

1. `data/shared.csv`, the faithful export of the collaboratively assembled XLSX.
2. `data/raw/06_sc_train_ib.zip`, the KazSAnDRA source archive.
3. `data/final_annotations.csv`, the preserved human-reviewed decisions for all 5,000 selected IDs. It stores the final label, split, row order, and text overrides for 33 records with differences from source text, including anonymization.

Run the following from the project directory to create a separate reconstruction while keeping the reviewed working file available for comparison.

```powershell
python scripts/prepare_dataset.py --output data/reconstructed.csv
```

This optional source-reconstruction command requires both raw inputs, which are excluded from Git. The ZIP has a public download link above; shared.csv currently has no public download link and must be supplied separately. A repository-only checkout can train directly on the included reviewed CSV. The reconstruction result contains exactly `id,text,label,split` and matches the reviewed records and row order. The output file must not already exist.

Raw inputs retain their original labels, columns, and personal data. The final annotations determine the output labels and split, and text overrides preserve reviewed edits. Historical keyword scripts and the TXT list are not part of this final reconstruction command. After further manual edits to the working CSV, update the annotation snapshot before claiming exact reconstruction.

The initial selection and draft relabeling scripts are retained locally and excluded from Git. The submitted preparation script is `scripts/prepare_dataset.py`, which reconstructs the final reviewed snapshot. Anonymization and grouped-splitting helpers are also included. Training and inference use the final four-column working CSV.

## 2. Train one classification model

### Model and input representation

The selected model is [Kaz-RoBERTa Conversational](https://huggingface.co/kz-transformers/kaz-roberta-conversational), a pretrained six-layer encoder with approximately 83.5 million parameters. Its byte-level BPE tokenizer has a vocabulary of 52,000 tokens. A two-class sequence-classification head is initialized for this task, and the full model is fine-tuned.

The model was chosen for its Kazakh and conversational pretraining and ability to use sentence context. Raw spelling, punctuation, masking, and language mixing are preserved. The tokenizer encodes uncommon strings as byte-level subwords. Inputs are truncated to 128 tokens including special tokens, so a profane expression beyond the retained prefix can be missed. Batches are dynamically padded, with CUDA padding rounded to a multiple of eight.

| Setting | Value |
| --- | --- |
| Random seed | 42 |
| Epochs | 3 |
| Batch size | 8 |
| Maximum input length | 128 tokens |
| Optimizer | AdamW |
| Learning rate | 0.00002 |
| Weight decay | 0.01 |
| Objective | Two-class cross-entropy |
| Precision | FP16 automatic mixed precision on CUDA |
| Checkpoint selection | Highest validation F1 for class 1 |
| Threshold selection | Highest validation F1 after each epoch |

Ties retain the earlier checkpoint. Training shuffling is seeded. Exact numerical agreement can vary with hardware and library versions. `run.json` stores settings, versions, the selected epoch, threshold, and validation metrics.

### Local setup

The checked environment uses Windows, Python 3.13.1, and an NVIDIA RTX 3060 Laptop GPU with 6 GB VRAM. Exact direct dependency versions are in `requirements.txt`. PyTorch is pinned to the CUDA 12.8 build installed in the project environment.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install jupyterlab ipykernel
.\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
.\.venv\Scripts\python.exe -m jupyterlab Bonus.ipynb
```

Select the project `.venv` kernel. CPU execution is supported by the notebook but will be slower. The published pretrained weights are downloaded on the first training run and cached under `artifacts/hf-cache`.

### Run training

Open `Bonus.ipynb` and execute the cells in order through **Run training**. The notebook loads the CSV, checks basic validity, fine-tunes the model on `train`, and selects settings using `val`. Leave `RUN_FINAL_TEST = False` during development. Use a new `MODEL_DIR` for the final run so that its artifacts can be distinguished from the earlier draft.

The checkpoint directory contains model weights, model configuration, tokenizer files, and `run.json`. Both the tokenizer and the threshold are required for inference.

## 3. Evaluate the result

### Recorded validation and test results

The selected checkpoint is stored in `artifacts/kaz-roberta-reviewed`. Epoch 1 had the highest validation F1 among the three training epochs. The saved threshold is 0.354868. The dataset SHA-256 is `8347b930ee426de579e06a89355f658062b0773446baafb5862dca0670f1ed41`.

| Metric | Validation | Test with revised reference labels |
| --- | ---: | ---: |
| Precision, class 1 | 0.9586 | 0.9145 |
| Recall, class 1 | 0.9653 | 0.9392 |
| F1, class 1 | 0.9619 | 0.9267 |
| Examples | 500 | 500 |

| Epoch | Training loss | Validation F1 |
| --- | ---: | ---: |
| 1 | 0.2064 | 0.9619 |
| 2 | 0.0696 | 0.9492 |
| 3 | 0.0264 | 0.9524 |

The test confusion matrix has reference labels in rows and predicted labels in columns.

| Reference / Prediction | 0 | 1 |
| --- | ---: | ---: |
| 0 | 339 | 13 |
| 1 | 9 | 139 |

There are 13 false positives and 9 false negatives. The source files are `run.json`, `test_metrics.json`, and `test_predictions.csv` in the selected checkpoint directory.

The first evaluation against the earlier reference labels gave precision 0.8947, recall 0.9379, and F1 0.9158. After inspecting those predictions, I corrected three test labels from 0 to 1. The reported revised result is precision 0.9145, recall 0.9392, and F1 0.9267. Train and validation examples, the selected epoch, and the threshold stayed the same. This is evaluation against corrected annotations after test inspection, rather than a new independent blind test.

### Error analysis

The following examples are taken from the saved test predictions. Explanations are hypotheses based on the input and output, and have not been established by attribution experiments.

| Test example | Reference | Prediction | Score for class 1 | Likely explanation | Practical improvement |
| --- | ---: | ---: | ---: | --- | --- |
| Мал сататын жерекен сатып алатын емес бағалары сұмдыққо. | 0 | 1 | 0.9167 | The reference uses mal literally for livestock. The model may associate this word with the insulting examples included in class 1. | Add reviewed neutral livestock and marketplace examples with the same vocabulary. |
| Күшті базар жоқ малатца 👍👍👍👍 | 0 | 1 | 0.7660 | The positive review contains a spelling of a Russian praise word. Its character or subword overlap with mal may contribute to the false positive. | Add neutral praise spellings as hard negatives and review tokenizer segmentation. |
| Амбастар | 1 | 0 | 0.0412 | The model misses a short obscene form. Sparse exposure to this inflection or limited context may explain the low score. | Collect additional real examples of this word family and review their labels. |
| Сигем жалептер | 1 | 0 | 0.1632 | The text contains target expressions, but the score remains below the validation-selected threshold. Spelling variation and limited training coverage are plausible causes. | Expand real training coverage of these expressions and their spelling variants. |
| ... 667. ... | 1 | 0 | 0.0144 | The long review ends with the project-specific numeric curse marker. The 128-token prefix may exclude the marker; this explanation requires checking the exact tokenization. | Measure truncation on long reviews and investigate longer inputs or window-based prediction using validation data. |

The errors show difficulty distinguishing literal or neutral word usage from insulting usage, recognizing rare short forms, and handling longer reviews. Proposed changes should be selected on validation data. The already inspected test set should be treated as an observed benchmark; further tuning would require a fresh independent evaluation set.

### Final evaluation procedure

After freezing annotation rules and retraining on the current split, set `RUN_FINAL_TEST = True` in the final notebook cell. Evaluate the selected checkpoint once on the 500 held-out test reviews. The notebook saves `test_metrics.json` with precision, recall, F1, confusion matrix, and example count, and prints misclassified examples.

A false positive flags a review without target Kazakh profanity. It can unfairly hide criticism or neutral product discussion. A false negative misses target profanity and lets it through moderation. The validation threshold controls this tradeoff. A human review queue can be more appropriate than automatic removal.

The recorded metrics and five concrete error examples are reported above. Preserve their dataset version and evaluation history when presenting the results.

## 4. Load the trained model and predict

The complete checkpoint lives in `artifacts/kaz-roberta-reviewed`. The 334 MB `model.safetensors` is tracked with Git LFS through `.gitattributes`; the remaining checkpoint files use ordinary Git. After this repository and its LFS objects have been pushed, a Git LFS clone provides all files required for inference.

Install Git LFS, then run these commands from the project directory when creating and uploading the repository:

```powershell
git init
git lfs install
git add .
git lfs ls-files
git commit -m "Add Kazakh profanity classifier"
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin HEAD
```

Before committing, verify that `git lfs ls-files` lists the trained model. Replace the remote placeholder with your repository URL. If the repository already has commits or a remote, use its existing setup.

To download the published project:

```powershell
git lfs install
git clone https://github.com/Tarantul4444/DLBonus.git
cd DLBonus
git lfs pull
```

Use https://github.com/Tarantul4444/DLBonus.git as the repository URL. A small LFS pointer file alone is insufficient for model loading; `git lfs pull` must retrieve the actual weights.

With the complete saved directory available, open `Bonus.ipynb` and run **Imports**, **Configuration**, **Load checkpoint**, **Predict review**, and the prediction example. Set `MODEL_DIR` to the downloaded checkpoint directory. No retraining is needed for these cells.

```python
predict("Тауар сипаттамаға сай келмеді.")
```

The function returns `label` and `score_class_1`. The score is the class 1 softmax output, with the saved validation-selected decision threshold. Calibration has not been evaluated.

## Files

| Path | Purpose |
| --- | --- |
| `Bonus.ipynb` | Training, validation, saved-model inference, final evaluation |
| `requirements.txt` | Pinned direct dependencies |
| `data/kazakh_profanity.csv` | Authoritative 5,000-review annotated snapshot |
| `data/final_annotations.csv` | Final reviewed labels, splits, row order, and text overrides |
| `data/shared.csv` | Local faithful export of the collaboratively assembled XLSX |
| `data/raw/06_sc_train_ib.zip` | Local KazSAnDRA source archive |
| `data/SOURCES.md` | Source provenance and access details |
| `data/kazakh-only-labeling.md` | Annotation rules and review limitations |
| `scripts/` | Final snapshot reconstruction, anonymization, and grouped splitting |
| `artifacts/kaz-roberta-reviewed/` | Metrics, predictions, settings, tokenizer, and model weights tracked through Git LFS |

## Limitations and practical improvements

Although I manually reviewed all records, subjective or inconsistent judgments can remain in ambiguous expressions. The insulting-word boundary is broader than a strict obscene-word definition. Candidate selection favors known vocabulary and therefore biases evaluation toward recognizable lexical forms. Reviews from apps and services do not fully represent physical-goods moderation. Language filtering uses simple heuristics, and unusual transliteration or unseen masking can be missed. The small test set limits precision of reported metrics. A larger independently reviewed product-review test set, consistent annotation adjudication, and longer-input handling are practical improvements.
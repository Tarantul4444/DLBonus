# Predict your own sentence

You need the project Python environment and the complete saved model in `artifacts/kaz-roberta-reviewed`, including the weights, tokenizer, configuration, and `run.json`.

If you cloned the repository, download the model weights with `git lfs pull`. Install dependencies using the setup instructions in `README.md` and select the `.venv` kernel in `Bonus.ipynb`.

Run these notebook cells in order:

1. **Imports** — the first code cell, starting with `import csv`.
2. **Configuration** — the code cell under **Configuration and device check**, starting with `ROOT = Path.cwd()`.
3. **Load checkpoint** — under **Load the saved model and predict a new review**, starting with `run = json.loads(...)`.
4. **Predict review** — the next code cell, defining `predict(text)`.
5. **Prediction example** — replace the example text with your sentence and run the cell.

```python
predict("Write your Kazakh or mixed-language sentence here.")
```

The result contains `label` (`0` or `1`) and `score_class_1` (the model's score for Kazakh profanity). The saved validation threshold determines the label.

Training, dataset loading, and final-test cells are unnecessary for this prediction workflow.

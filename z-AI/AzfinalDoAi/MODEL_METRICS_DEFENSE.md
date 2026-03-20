# Station1 DO Model Metrics (Defense Notes)

## 1) Model and Task Summary
- Model file: `station1_random_classifier_compact.pkl`
- Training script: `station1_random_classifier_improved.py`
- Task type: **Classification** (DO range prediction), not direct regression
- Classes:
  - Critical: DO < 5
  - Low: 5 <= DO < 6
  - Warning: 6 <= DO < 7
  - Normal: DO >= 7
- Safety policy after class-to-DO mapping:
  - If predicted DO is in [6, 7), subtract 1.0

## 2) Confirmed Evaluation Results

### A. Fixed split evaluation (seed=42, 20% holdout)
Source: `show_example_result.py` / `verify_model_performance.py`
- Accuracy: **85.97%**
- F1-macro: **74.92%**
- F1-weighted: **84.96%**
- R2 (class output forced back to DO value): **-0.1923** (-19.23%)

Per-class report (fixed split):
- Critical: precision 0.79, recall 0.95, f1 0.87
- Low: precision 0.86, recall 0.52, f1 0.65
- Warning: precision 0.66, recall 0.49, f1 0.56
- Normal: precision 0.89, recall 0.96, f1 0.92

### B. Training artifact summary (dynamic runs)
Source: `show_artifact_metadata.py`
- Accuracy mean: **75.40%**
- Accuracy std: **0.20%**
- F1-macro mean: **47.67%**
- F1-macro std: **0.95%**
- Critical recall mean: **80.24%**
- Best run (selected by F1-macro):
  - Accuracy: 75.35%
  - F1-macro: 48.47%

### C. Regression reference (separate experiment)
Source: `boost_r2_search.log`
- Best R2 in that search: **42.79%**
- Corresponding RMSE: **3.449**
- Corresponding MAE: **2.614**
- Conclusion: Regression R2 remained around low-40% on this dataset

## 3) What Each Metric Means (Defense Friendly)
- Accuracy:
  - Percent of all predictions that are correct.
  - Easy to understand, but can hide poor performance on smaller classes.

- Precision:
  - Of all samples predicted as a class, how many were correct.
  - High precision means fewer false alarms for that class.

- Recall:
  - Of all true samples in a class, how many the model found.
  - For safety, recall on Critical class is very important.

- F1 score:
  - Harmonic mean of precision and recall.
  - Good when class distribution is imbalanced.

- F1-macro:
  - Average F1 across classes, each class weighted equally.
  - Better indicator of balanced performance across Critical/Low/Warning/Normal.

- F1-weighted:
  - Average F1 weighted by class frequency.
  - Usually higher when majority class performance is strong.

- RMSE (Regression):
  - Root mean squared error in original DO units.
  - Penalizes large errors more strongly.

- MAE (Regression):
  - Mean absolute error in DO units.
  - Direct average absolute error size.

- R2 (Regression):
  - Variance explained by regression model.
  - 1.0 is perfect, 0.0 means no improvement over mean prediction.
  - Negative means worse than simply predicting the mean.

## 4) Why R2 Can Be Negative Here While Classification Is Good
- This model is trained to predict **classes**, not exact DO values.
- Converting class predictions back to fixed DO values (4.5, 5.5, 6.5, 8.0 + policy) is coarse.
- That coarse mapping can produce poor continuous-fit R2 even when class labels are accurate.
- So:
  - Use **Accuracy/F1** to judge classification quality.
  - Use **RMSE/MAE/R2** only for dedicated regression models.

## 5) Recommended Defense Talking Points
- "Our deployment model is a range-based classifier designed for operational decisions, not exact DO regression."
- "On fixed holdout evaluation, we reached 85.97% accuracy and 74.92% macro-F1."
- "Critical recall is high (95% in fixed split, 80.24% mean across dynamic runs), which supports safety-oriented monitoring."
- "Negative R2 from class-to-DO mapping is expected because class outputs are discretized and include conservative policy adjustment."
- "For exact numeric DO estimation, a separate regression model should be evaluated with RMSE/MAE/R2."

## 6) Quick Repro Commands
From the project where scripts exist:

```powershell
python station1_random_classifier_improved.py
python show_example_result.py
python show_artifact_metadata.py
python verify_model_performance.py
```

# Sample Prediction Results (Good / Warning / Danger)

- Source model: `station1_random_classifier_compact.pkl`
- Source data: `C:\Users\USER\Desktop\capstone\z-AI\DODO\model\station1Traing\withTimePondData_station1.csv`
- Split: dynamic holdout (test_size=0.2, split_seed=1943089852)
- Sampling mode: dynamic (new random rows each run)
- Label mapping used in this report:
  - Good: Normal
  - Warning: Warning
  - Danger: Critical + Low
- Pred DO Dynamic = calibrated DO from `do_calibrator` in model artifact
- Predicted class/result comes directly from the classifier in the `.pkl` model
- Requested rows per section: 10

## Good (10 samples)

- Group match rate (Predicted Result vs Actual Result): **100.00%**

| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |
|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|
| 1 | 8.2747 | 0.0359 | 26.1253 | 18.4042 | 18.6848 | Good | Good | Excellent | 12.9583 | Yes |
| 2 | 8.0244 | 0.0400 | 23.6264 | 15.1125 | 7.7405 | Good | Good | Excellent | 12.0274 | Yes |
| 3 | 5.8000 | 0.0890 | 28.0900 | 21.0000 | 7.8000 | Good | Good | Good | 6.9051 | Yes |
| 4 | 5.6000 | 0.0820 | 24.0500 | 34.1000 | 6.7000 | Good | Good | Good | 9.5890 | Yes |
| 5 | 8.4829 | 0.0154 | 20.4239 | 20.0455 | 15.9365 | Good | Good | Excellent | 11.1258 | Yes |
| 6 | 5.2000 | 0.0910 | 26.3900 | 30.6000 | 9.6000 | Good | Good | Good | 8.0619 | Yes |
| 7 | 5.5486 | 0.0262 | 26.6060 | 21.2020 | 11.3575 | Good | Good | Excellent | 12.8429 | Yes |
| 8 | 8.1482 | 0.0233 | 30.1691 | 15.8230 | 11.7058 | Good | Good | Excellent | 12.4888 | Yes |
| 9 | 5.6000 | 0.0710 | 30.1300 | 27.7000 | 7.8000 | Good | Good | Good | 6.6501 | Yes |
| 10 | 6.9879 | 0.0411 | 19.2207 | 31.2208 | 12.4911 | Good | Good | Excellent | 12.7906 | Yes |

## Warning (10 samples)

- Group match rate (Predicted Result vs Actual Result): **100.00%**

| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |
|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|
| 1 | 6.4000 | 0.3800 | 35.2500 | 29.0000 | 4.4502 | Warning | Warning | Fair | 4.8278 | Yes |
| 2 | 5.8000 | 0.2510 | 31.6900 | 21.9000 | 4.9560 | Warning | Warning | Fair | 4.8963 | Yes |
| 3 | 6.1000 | 0.1250 | 32.7300 | 23.4000 | 4.3116 | Warning | Warning | Fair | 4.9442 | Yes |
| 4 | 7.0000 | 0.0800 | 22.9400 | 30.0000 | 4.3000 | Warning | Warning | Fair | 4.4874 | Yes |
| 5 | 5.9318 | 0.0275 | 26.3654 | 38.8332 | 5.3513 | Warning | Warning | Fair | 9.6863 | Yes |
| 6 | 6.0171 | 0.0172 | 19.4382 | 38.6107 | 5.0868 | Warning | Warning | Fair | 9.1679 | Yes |
| 7 | 6.0000 | 0.1220 | 33.6000 | 22.9000 | 4.0780 | Warning | Warning | Fair | 4.8879 | Yes |
| 8 | 5.8000 | 0.3430 | 32.4100 | 21.8000 | 4.1065 | Warning | Warning | Fair | 4.8794 | Yes |
| 9 | 6.2000 | 0.3210 | 33.4500 | 37.5000 | 5.0720 | Warning | Warning | Fair | 4.8288 | Yes |
| 10 | 6.6000 | 0.1090 | 35.0400 | 20.7000 | 4.8627 | Warning | Warning | Fair | 5.1622 | Yes |

## Danger (10 samples)

- Group match rate (Predicted Result vs Actual Result): **90.00%**

| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |
|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|
| 1 | 6.4000 | 0.0890 | 21.7600 | 29.2000 | 3.3000 | Danger | Danger | Poor | 3.8820 | Yes |
| 2 | 7.0000 | 0.0950 | 22.0900 | 31.9000 | 3.3000 | Danger | Danger | Poor | 4.0548 | Yes |
| 3 | 7.7000 | 0.0160 | 23.9600 | 22.0000 | 1.2000 | Danger | Danger | Danger | 1.7749 | Yes |
| 4 | 8.1000 | 0.0970 | 23.7400 | 28.0000 | 2.7000 | Danger | Danger | Poor | 2.7785 | Yes |
| 5 | 6.7000 | 0.0100 | 21.2500 | 33.2000 | 3.9000 | Danger | Danger | Poor | 4.1439 | Yes |
| 6 | 6.4000 | 0.0750 | 25.2500 | 34.4000 | 3.6000 | Danger | Warning | Fair | 6.2090 | No |
| 7 | 7.4000 | 0.0010 | 24.1000 | 22.7000 | 1.3000 | Danger | Danger | Danger | 2.3094 | Yes |
| 8 | 8.9000 | 0.0590 | 24.4500 | 27.1000 | 2.0000 | Danger | Danger | Danger | 1.4784 | Yes |
| 9 | 8.5000 | 0.0210 | 25.0800 | 23.1000 | 1.5000 | Danger | Danger | Danger | 1.4259 | Yes |
| 10 | 7.9000 | 0.0560 | 21.5100 | 27.9000 | 1.1000 | Danger | Danger | Danger | 1.7801 | Yes |

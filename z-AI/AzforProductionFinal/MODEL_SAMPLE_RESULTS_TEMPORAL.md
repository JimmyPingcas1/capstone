# Sample Prediction Results (Good / Warning / Danger)

- Source model: `station1_random_classifier_compact.pkl`
- Source data: `C:\Users\USER\Desktop\capstone\z-AI\DODO\model\station1Traing\withTimePondData_station1.csv`
- Split: dynamic holdout (test_size=0.2, split_seed=399430707)
- Sampling mode: **temporal (consecutive time-ordered rows for realistic gradual parameter changes)**
- Label mapping used in this report:
  - Good: Normal
  - Warning: Warning
  - Danger: Critical + Low
- Pred DO Dynamic = calibrated DO from `do_calibrator` in model artifact
- Predicted class/result comes directly from the classifier in the `.pkl` model
- Requested rows per section: 20

## Good (20 samples)

- Group match rate (Predicted Result vs Actual Result): **100.00%**

| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |
|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|
| 1 | 5.2000 | 0.0390 | 22.0300 | 24.1000 | 8.5000 | Good | Good | Excellent | 12.4689 | Yes |
| 2 | 5.4000 | 0.0130 | 24.6000 | 30.2000 | 9.5000 | Good | Good | Excellent | 12.3793 | Yes |
| 3 | 5.4000 | 0.0610 | 24.6700 | 29.8000 | 7.6000 | Good | Good | Good | 9.4736 | Yes |
| 4 | 5.0000 | 0.0130 | 24.6900 | 33.2000 | 6.8000 | Good | Good | Good | 9.4023 | Yes |
| 5 | 5.6000 | 0.0890 | 25.3800 | 26.7000 | 12.0000 | Good | Good | Good | 10.5621 | Yes |
| 6 | 5.7000 | 0.0760 | 24.1800 | 31.8000 | 8.8000 | Good | Good | Good | 9.6655 | Yes |
| 7 | 6.0000 | 0.0030 | 24.1200 | 19.7000 | 8.8000 | Good | Good | Excellent | 11.7028 | Yes |
| 8 | 6.0000 | 0.0920 | 24.0700 | 18.7000 | 9.1000 | Good | Good | Excellent | 11.1861 | Yes |
| 9 | 5.0000 | 0.0170 | 23.7100 | 26.1000 | 9.3000 | Good | Good | Excellent | 11.9666 | Yes |
| 10 | 5.1000 | 0.0900 | 23.4000 | 26.0000 | 10.8000 | Good | Good | Excellent | 11.5996 | Yes |
| 11 | 5.4000 | 0.0830 | 23.2400 | 25.9000 | 8.0000 | Good | Good | Good | 10.6394 | Yes |
| 12 | 5.7000 | 0.0980 | 22.4100 | 32.4000 | 12.0000 | Good | Good | Excellent | 12.4979 | Yes |
| 13 | 5.7000 | 0.0050 | 22.5300 | 20.9000 | 6.5000 | Good | Good | Excellent | 11.8755 | Yes |
| 14 | 5.1000 | 0.0020 | 22.1200 | 29.9000 | 9.2000 | Good | Good | Excellent | 11.9929 | Yes |
| 15 | 5.6000 | 0.0940 | 21.7900 | 31.1000 | 10.6000 | Good | Good | Excellent | 12.6494 | Yes |
| 16 | 5.3000 | 0.0190 | 21.6200 | 31.4000 | 10.1000 | Good | Good | Excellent | 13.0326 | Yes |
| 17 | 5.3000 | 0.0190 | 21.5000 | 33.6000 | 6.5000 | Good | Good | Excellent | 11.7591 | Yes |
| 18 | 5.4000 | 0.0610 | 21.9200 | 33.3000 | 11.7000 | Good | Good | Excellent | 13.1278 | Yes |
| 19 | 5.1000 | 0.0210 | 23.0600 | 24.3000 | 11.6000 | Good | Good | Excellent | 13.6450 | Yes |
| 20 | 6.0000 | 0.0610 | 22.1400 | 26.7000 | 6.2000 | Good | Good | Good | 9.2962 | Yes |

## Warning (20 samples)

- Group match rate (Predicted Result vs Actual Result): **50.00%**

| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |
|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|
| 1 | 6.7000 | 0.0650 | 21.9400 | 19.3000 | 5.3000 | Warning | Warning | Fair | 6.1075 | Yes |
| 2 | 6.5000 | 0.0550 | 21.7500 | 20.3000 | 4.2000 | Warning | Danger | Poor | 4.3128 | No |
| 3 | 6.4000 | 0.0410 | 21.3600 | 19.0000 | 5.2000 | Warning | Warning | Fair | 4.5016 | Yes |
| 4 | 6.9000 | 0.0170 | 21.5500 | 30.3000 | 4.8000 | Warning | Danger | Poor | 4.3821 | No |
| 5 | 7.2000 | 0.0190 | 23.3900 | 34.4000 | 5.0000 | Warning | Warning | Fair | 4.9015 | Yes |
| 6 | 7.2000 | 0.0500 | 25.2700 | 30.8000 | 4.0000 | Warning | Warning | Fair | 4.3854 | Yes |
| 7 | 7.1000 | 0.0380 | 25.2600 | 29.9000 | 5.2000 | Warning | Warning | Fair | 4.5569 | Yes |
| 8 | 7.0000 | 0.0830 | 24.6900 | 18.9000 | 5.4000 | Warning | Danger | Poor | 4.0912 | No |
| 9 | 6.7000 | 0.0130 | 24.1800 | 29.8000 | 5.3000 | Warning | Warning | Fair | 4.5457 | Yes |
| 10 | 6.9000 | 0.1000 | 24.1400 | 23.8000 | 4.1000 | Warning | Danger | Poor | 4.0608 | No |
| 11 | 7.1000 | 0.0230 | 23.2200 | 33.7000 | 4.4000 | Warning | Warning | Fair | 4.7145 | Yes |
| 12 | 6.4000 | 0.0110 | 22.5500 | 28.7000 | 4.7000 | Warning | Warning | Fair | 4.2699 | Yes |
| 13 | 6.5000 | 0.0380 | 22.4200 | 31.2000 | 5.2000 | Warning | Danger | Poor | 4.0496 | No |
| 14 | 6.1000 | 0.0120 | 22.3200 | 31.4000 | 4.6000 | Warning | Warning | Fair | 4.4447 | Yes |
| 15 | 6.1000 | 0.0870 | 22.5700 | 20.6000 | 4.1000 | Warning | Warning | Fair | 4.1714 | Yes |
| 16 | 6.7000 | 0.0450 | 22.9000 | 20.4000 | 5.1000 | Warning | Danger | Poor | 4.1594 | No |
| 17 | 7.2000 | 0.0820 | 25.7900 | 24.5000 | 4.3000 | Warning | Danger | Poor | 4.1410 | No |
| 18 | 7.0000 | 0.0470 | 25.6100 | 24.2000 | 4.3000 | Warning | Danger | Poor | 4.2886 | No |
| 19 | 6.9000 | 0.0370 | 25.3700 | 23.9000 | 4.2000 | Warning | Danger | Poor | 4.4360 | No |
| 20 | 7.2000 | 0.0640 | 24.3300 | 27.2000 | 4.5000 | Warning | Danger | Poor | 4.0785 | No |

## Danger (20 samples)

- Group match rate (Predicted Result vs Actual Result): **100.00%**

| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |
|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|
| 1 | 6.6000 | 0.0510 | 21.5300 | 28.6000 | 3.4000 | Danger | Danger | Poor | 3.8740 | Yes |
| 2 | 6.1000 | 0.0460 | 21.7700 | 27.3000 | 3.9000 | Danger | Danger | Poor | 4.3538 | Yes |
| 3 | 6.4000 | 0.0110 | 22.3200 | 24.4000 | 3.4000 | Danger | Danger | Poor | 4.1767 | Yes |
| 4 | 7.2000 | 0.0740 | 23.4500 | 28.7000 | 3.0000 | Danger | Danger | Poor | 3.8881 | Yes |
| 5 | 6.5000 | 0.0420 | 22.4100 | 24.2000 | 3.5000 | Danger | Danger | Poor | 3.9398 | Yes |
| 6 | 6.7000 | 0.0330 | 21.9400 | 19.1000 | 3.6000 | Danger | Danger | Poor | 4.3506 | Yes |
| 7 | 6.4000 | 0.0490 | 22.1300 | 21.1000 | 3.2000 | Danger | Danger | Poor | 3.9420 | Yes |
| 8 | 6.8000 | 0.0050 | 22.1100 | 29.4000 | 3.3000 | Danger | Danger | Poor | 4.1315 | Yes |
| 9 | 6.5000 | 0.0280 | 23.5900 | 29.9000 | 3.4000 | Danger | Danger | Poor | 3.9350 | Yes |
| 10 | 6.3000 | 0.0860 | 25.0700 | 32.0000 | 3.8000 | Danger | Danger | Poor | 4.2368 | Yes |
| 11 | 6.9000 | 0.0850 | 23.9200 | 20.0000 | 3.6000 | Danger | Danger | Poor | 4.2812 | Yes |
| 12 | 7.2000 | 0.0390 | 23.0300 | 25.0000 | 3.6000 | Danger | Danger | Poor | 4.0291 | Yes |
| 13 | 6.4000 | 0.0440 | 23.4400 | 27.6000 | 3.0000 | Danger | Danger | Poor | 4.2079 | Yes |
| 14 | 6.5000 | 0.0130 | 22.9000 | 19.9000 | 3.5000 | Danger | Danger | Poor | 3.9710 | Yes |
| 15 | 6.7000 | 0.0350 | 28.6900 | 24.6000 | 3.6000 | Danger | Danger | Poor | 4.7762 | Yes |
| 16 | 6.9000 | 0.0340 | 20.8200 | 29.7000 | 3.3000 | Danger | Danger | Poor | 5.1257 | Yes |
| 17 | 7.1000 | 0.0010 | 20.0900 | 20.8000 | 3.2000 | Danger | Danger | Poor | 4.4230 | Yes |
| 18 | 7.1000 | 0.0930 | 29.1200 | 28.4000 | 3.0000 | Danger | Danger | Poor | 4.1027 | Yes |
| 19 | 6.5000 | 0.0730 | 24.0500 | 25.8000 | 3.8000 | Danger | Danger | Poor | 4.5223 | Yes |
| 20 | 6.9000 | 0.0680 | 29.0600 | 26.7000 | 3.8000 | Danger | Danger | Poor | 3.9515 | Yes |

# Sample Prediction Results (Good / Warning / Danger)

- Source model: `station1_random_classifier_compact.pkl`
- Source data: `C:\Users\USER\Desktop\capstone\z-AI\DODO\model\station1Traing\withTimePondData_station1.csv`
- Split: dynamic holdout (test_size=0.2, split_seed=1787093992)
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
| 1 | 5.1000 | 0.0450 | 21.2400 | 28.3000 | 9.8000 | Good | Good | Excellent | 12.7510 | Yes |
| 2 | 5.3000 | 0.0570 | 24.1000 | 32.0000 | 11.5000 | Good | Good | Excellent | 11.6238 | Yes |
| 3 | 5.8000 | 0.0530 | 24.7000 | 29.1000 | 6.1000 | Good | Good | Good | 9.3498 | Yes |
| 4 | 5.0000 | 0.0910 | 25.7800 | 29.9000 | 11.2000 | Good | Good | Good | 10.3232 | Yes |
| 5 | 5.2000 | 0.0500 | 24.7300 | 21.5000 | 7.2000 | Good | Good | Good | 8.7208 | Yes |
| 6 | 5.7000 | 0.0770 | 21.6700 | 27.7000 | 6.7000 | Good | Good | Excellent | 13.2220 | Yes |
| 7 | 5.0000 | 0.0640 | 21.5500 | 20.7000 | 8.6000 | Good | Good | Excellent | 12.7751 | Yes |
| 8 | 5.3000 | 0.0190 | 21.5000 | 33.6000 | 6.5000 | Good | Good | Excellent | 11.7591 | Yes |
| 9 | 5.8000 | 0.0390 | 21.5200 | 24.0000 | 10.1000 | Good | Good | Excellent | 11.7323 | Yes |
| 10 | 5.1000 | 0.0210 | 23.0600 | 24.3000 | 11.6000 | Good | Good | Excellent | 13.6450 | Yes |
| 11 | 5.5000 | 0.0300 | 23.7600 | 20.5000 | 7.3000 | Good | Good | Good | 9.9254 | Yes |
| 12 | 5.6000 | 0.0950 | 25.3400 | 21.5000 | 11.1000 | Good | Good | Good | 11.0600 | Yes |
| 13 | 5.7000 | 0.0710 | 25.7300 | 26.9000 | 10.0000 | Good | Good | Good | 10.0899 | Yes |
| 14 | 5.1000 | 0.0140 | 25.7400 | 19.4000 | 10.7000 | Good | Good | Good | 10.0035 | Yes |
| 15 | 5.4000 | 0.0090 | 25.6100 | 29.6000 | 6.5000 | Good | Good | Good | 9.4914 | Yes |
| 16 | 5.5000 | 0.0590 | 25.5400 | 30.7000 | 6.7000 | Good | Good | Good | 8.8160 | Yes |
| 17 | 5.3000 | 0.0170 | 24.1300 | 19.1000 | 7.7000 | Good | Good | Good | 10.0762 | Yes |
| 18 | 5.5000 | 0.0300 | 23.8500 | 34.3000 | 9.1000 | Good | Good | Excellent | 11.7716 | Yes |
| 19 | 5.9000 | 0.0700 | 23.0700 | 29.1000 | 10.3000 | Good | Good | Excellent | 11.7680 | Yes |
| 20 | 5.1000 | 0.0560 | 22.2200 | 30.1000 | 9.8000 | Good | Good | Excellent | 12.3846 | Yes |

## Warning (20 samples)

- Group match rate (Predicted Result vs Actual Result): **80.00%**

| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |
|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|
| 1 | 6.7000 | 0.0650 | 21.9400 | 19.3000 | 5.3000 | Warning | Warning | Fair | 6.1075 | Yes |
| 2 | 6.5000 | 0.0760 | 21.8300 | 30.7000 | 4.9000 | Warning | Warning | Fair | 4.7918 | Yes |
| 3 | 6.9000 | 0.0100 | 21.2400 | 31.5000 | 4.8000 | Warning | Warning | Fair | 4.4429 | Yes |
| 4 | 6.5000 | 0.0150 | 21.3100 | 30.1000 | 4.2000 | Warning | Warning | Fair | 4.3615 | Yes |
| 5 | 6.6000 | 0.0680 | 21.3500 | 20.7000 | 4.8000 | Warning | Warning | Fair | 4.2720 | Yes |
| 6 | 6.5000 | 0.0210 | 21.4200 | 19.8000 | 4.3000 | Warning | Warning | Fair | 4.4080 | Yes |
| 7 | 7.2000 | 0.0190 | 23.3900 | 34.4000 | 5.0000 | Warning | Warning | Fair | 4.9015 | Yes |
| 8 | 7.0000 | 0.0910 | 23.4000 | 23.2000 | 5.3000 | Warning | Danger | Poor | 4.0516 | No |
| 9 | 7.1000 | 0.0130 | 25.5600 | 23.8000 | 4.3000 | Warning | Warning | Fair | 5.2036 | Yes |
| 10 | 6.6000 | 0.0090 | 22.9500 | 20.7000 | 4.4000 | Warning | Warning | Fair | 4.3409 | Yes |
| 11 | 7.1000 | 0.0390 | 22.9900 | 31.3000 | 4.0000 | Warning | Warning | Fair | 4.4078 | Yes |
| 12 | 7.0000 | 0.0220 | 24.7600 | 28.5000 | 4.0000 | Warning | Warning | Fair | 4.4888 | Yes |
| 13 | 7.2000 | 0.0710 | 24.5200 | 24.2000 | 4.7000 | Warning | Warning | Fair | 4.5126 | Yes |
| 14 | 6.7000 | 0.0230 | 24.3700 | 34.0000 | 4.1000 | Warning | Warning | Fair | 4.7601 | Yes |
| 15 | 6.2000 | 0.0540 | 22.4900 | 31.5000 | 5.0000 | Warning | Danger | Poor | 4.1755 | No |
| 16 | 7.1000 | 0.0780 | 21.2400 | 23.4000 | 4.1000 | Warning | Danger | Poor | 4.1710 | No |
| 17 | 6.7000 | 0.0670 | 22.1600 | 32.9000 | 5.4000 | Warning | Warning | Fair | 4.4093 | Yes |
| 18 | 6.1000 | 0.0520 | 22.8100 | 32.1000 | 4.4000 | Warning | Warning | Fair | 4.3189 | Yes |
| 19 | 7.1000 | 0.0490 | 25.9200 | 25.7000 | 5.4000 | Warning | Warning | Fair | 4.8764 | Yes |
| 20 | 7.0000 | 0.0470 | 25.6100 | 24.2000 | 4.3000 | Warning | Danger | Poor | 4.2886 | No |

## Danger (20 samples)

- Group match rate (Predicted Result vs Actual Result): **80.00%**

| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |
|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|
| 1 | 6.3000 | 0.0690 | 21.1300 | 33.4000 | 3.3000 | Danger | Danger | Poor | 4.0740 | Yes |
| 2 | 6.4000 | 0.0110 | 22.3200 | 24.4000 | 3.4000 | Danger | Danger | Poor | 4.1767 | Yes |
| 3 | 6.8000 | 0.0480 | 24.8800 | 28.5000 | 3.3000 | Danger | Danger | Poor | 4.0972 | Yes |
| 4 | 6.8000 | 0.0200 | 23.2500 | 34.2000 | 3.3000 | Danger | Warning | Fair | 5.3809 | No |
| 5 | 7.0000 | 0.0980 | 22.6800 | 21.1000 | 3.3000 | Danger | Danger | Poor | 3.9246 | Yes |
| 6 | 6.2000 | 0.1000 | 24.7700 | 22.7000 | 3.7000 | Danger | Danger | Poor | 3.8893 | Yes |
| 7 | 6.4000 | 0.0750 | 25.2500 | 34.4000 | 3.6000 | Danger | Warning | Fair | 6.2090 | No |
| 8 | 6.4000 | 0.0710 | 22.7600 | 31.0000 | 3.2000 | Danger | Danger | Poor | 3.8901 | Yes |
| 9 | 7.2000 | 0.0190 | 21.1800 | 28.6000 | 3.6000 | Danger | Danger | Poor | 5.1912 | Yes |
| 10 | 6.5000 | 0.0760 | 22.7100 | 21.4000 | 3.4000 | Danger | Danger | Poor | 3.8700 | Yes |
| 11 | 6.4000 | 0.0060 | 24.9300 | 34.3000 | 3.1000 | Danger | Warning | Fair | 5.7078 | No |
| 12 | 6.8000 | 0.0020 | 24.6200 | 31.7000 | 3.1000 | Danger | Danger | Poor | 4.1983 | Yes |
| 13 | 6.9000 | 0.0500 | 24.6300 | 33.9000 | 3.5000 | Danger | Warning | Fair | 4.5621 | No |
| 14 | 6.8000 | 0.0410 | 24.8900 | 32.9000 | 3.1000 | Danger | Danger | Poor | 4.1417 | Yes |
| 15 | 6.5000 | 0.0210 | 23.9200 | 30.3000 | 3.8000 | Danger | Danger | Poor | 4.1636 | Yes |
| 16 | 6.9000 | 0.0430 | 28.9700 | 19.8000 | 3.4000 | Danger | Danger | Poor | 4.4476 | Yes |
| 17 | 6.5000 | 0.0300 | 23.0900 | 29.9000 | 3.3000 | Danger | Danger | Poor | 5.3969 | Yes |
| 18 | 6.7000 | 0.0350 | 28.6900 | 24.6000 | 3.6000 | Danger | Danger | Poor | 4.7762 | Yes |
| 19 | 6.1000 | 0.0430 | 22.7200 | 25.1000 | 3.5000 | Danger | Danger | Poor | 4.3669 | Yes |
| 20 | 7.1000 | 0.0930 | 29.1200 | 28.4000 | 3.0000 | Danger | Danger | Poor | 4.1027 | Yes |

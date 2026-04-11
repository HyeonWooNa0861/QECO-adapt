# Comparison Verification Artifacts

This directory contains curated comparison outputs used by the QECO-ADAPT manuscript. The repository intentionally tracks only paper-facing comparison artifacts and excludes raw per-algorithm run folders.

## Why These Files Are Tracked

The comparison artifacts are tracked for three reasons.

- `comparison_finals.csv` and `comparison_finals.json` provide the final 10% episode-window values used in the manuscript tables.
- `comparison_finals.png` and `comparison_timeseries_smoothed.png` provide the scenario-level figures rendered in the manuscript.
- `comparison_runtime.png` and `runtime_summary.csv` provide runtime evidence for the runtime discussion and the CD exclusion argument.

## Main Scenario Artifacts

| Scenario | Setting | Final CSV | Final Figure | Smoothed Time-Series | Runtime Figure | Summary JSON |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | users=10, edges=1 | [CSV](./user_10_ep_400_edge_1/comparison_finals.csv) | [Final](./user_10_ep_400_edge_1/comparison_finals.png) | [Time-series](./user_10_ep_400_edge_1/comparison_timeseries_smoothed.png) | [Runtime](./user_10_ep_400_edge_1/comparison_runtime.png) | [JSON](./user_10_ep_400_edge_1/comparison_summary.json) |
| S2 | users=30, edges=1 | [CSV](./user_30_ep_400_edge_1/comparison_finals.csv) | [Final](./user_30_ep_400_edge_1/comparison_finals.png) | [Time-series](./user_30_ep_400_edge_1/comparison_timeseries_smoothed.png) | [Runtime](./user_30_ep_400_edge_1/comparison_runtime.png) | [JSON](./user_30_ep_400_edge_1/comparison_summary.json) |
| S3 | users=30, edges=3 | [CSV](./user_30_ep_400_edge_3/comparison_finals.csv) | [Final](./user_30_ep_400_edge_3/comparison_finals.png) | [Time-series](./user_30_ep_400_edge_3/comparison_timeseries_smoothed.png) | [Runtime](./user_30_ep_400_edge_3/comparison_runtime.png) | [JSON](./user_30_ep_400_edge_3/comparison_summary.json) |
| S4 | users=50, edges=1 | [CSV](./user_50_ep_400_edge_1/comparison_finals.csv) | [Final](./user_50_ep_400_edge_1/comparison_finals.png) | [Time-series](./user_50_ep_400_edge_1/comparison_timeseries_smoothed.png) | [Runtime](./user_50_ep_400_edge_1/comparison_runtime.png) | [JSON](./user_50_ep_400_edge_1/comparison_summary.json) |
| S5 | users=50, edges=10 | [CSV](./user_50_ep_400_edge_10/comparison_finals.csv) | [Final](./user_50_ep_400_edge_10/comparison_finals.png) | [Time-series](./user_50_ep_400_edge_10/comparison_timeseries_smoothed.png) | [Runtime](./user_50_ep_400_edge_10/comparison_runtime.png) | [JSON](./user_50_ep_400_edge_10/comparison_summary.json) |
| S6 | users=80, edges=1 | [CSV](./user_80_ep_400_edge_1/comparison_finals.csv) | [Final](./user_80_ep_400_edge_1/comparison_finals.png) | [Time-series](./user_80_ep_400_edge_1/comparison_timeseries_smoothed.png) | [Runtime](./user_80_ep_400_edge_1/comparison_runtime.png) | [JSON](./user_80_ep_400_edge_1/comparison_summary.json) |
| S7 | users=80, edges=3 | [CSV](./user_80_ep_400_edge_3/comparison_finals.csv) | [Final](./user_80_ep_400_edge_3/comparison_finals.png) | [Time-series](./user_80_ep_400_edge_3/comparison_timeseries_smoothed.png) | [Runtime](./user_80_ep_400_edge_3/comparison_runtime.png) | [JSON](./user_80_ep_400_edge_3/comparison_summary.json) |

## Runtime Summary

The manuscript runtime discussion uses [runtime_summary.csv](./runtime_summary.csv). Runtime values are trimmed median episode runtimes in seconds.

| Scenario | Users | Edges | DROO | QECO | QECO-ADAPT | Tang&Wong DQN | Fastest |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| S1 | 10 | 1 | 1.4322 | 1.5699 | 1.6495 | 1.5264 | DROO |
| S2 | 30 | 1 | 3.5228 | 4.3848 | 4.2482 | 4.3461 | DROO |
| S3 | 30 | 3 | 3.5470 | 3.9403 | 3.9490 | 3.8265 | DROO |
| S4 | 50 | 1 | 8.1153 | 6.4818 | 7.1937 | 6.7177 | QECO |
| S5 | 50 | 10 | 9.4509 | 7.4879 | 8.1046 | 6.4098 | Tang&Wong DQN |
| S6 | 80 | 1 | 8.7433 | 9.5163 | 10.5473 | 10.2755 | DROO |
| S7 | 80 | 3 | 8.9307 | 9.6805 | 9.6528 | 9.5089 | DROO |

## Auxiliary CD Check

The folder [user_10_ep_400_edge_1__cd-qeco-qeco-adapt](./user_10_ep_400_edge_1__cd-qeco-qeco-adapt/) is retained as auxiliary evidence for excluding CD from the main comparison. In that setting, CD recorded `14.3218s` trimmed median episode runtime, while QECO and QECO-ADAPT recorded `1.4273s` and `1.4349s`.

## Supplementary But Not Main-Text Figures

The files `comparison_averages.png` and `comparison_timeseries.png` are retained as supplementary audit plots. The manuscript itself uses `comparison_finals.png`, `comparison_timeseries_smoothed.png`, the CSV/JSON summaries, and the runtime evidence.

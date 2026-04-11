# QECO-ADAPT MEC Offloading Study

This repository contains a shared mobile edge computing (MEC) evaluation setup for comparing DROO, QECO, QECO-ADAPT, and Tang&Wong-style DQN baselines.

The main paper draft is:

- `paper_draft_latest_comparison_kr.md`

## Main Commands

Run one common-environment algorithm:

```bash
python3 QECO_DROO.py --execute common-run qeco
python3 QECO_DROO.py --execute common-run qeco-adapt
python3 QECO_DROO.py --execute common-run droo
python3 QECO_DROO.py --execute common-run twdqn
```

Create comparison charts:

```bash
python3 QECO_DROO.py --execute compare
```

Create CD/QECO/QECO-ADAPT comparison:

```bash
python3 QECO_DROO.py --execute compare-cqa
```

Regenerate formula visualizations:

```bash
/home/wsl/Alpha_1/env_qeco/bin/python visualize_metric_formulas.py
/home/wsl/Alpha_1/env_qeco/bin/python visualize_adapt_formula.py
/home/wsl/Alpha_1/env_qeco/bin/python visualize_qeco_adapt_math_definitions.py
/home/wsl/Alpha_1/env_qeco/bin/python visualize_qeco_adapt_constant_calibration.py
```

## Repository Layout

- `QECO_DROO.py`: CLI wrapper for setup, common runs, and comparison generation.
- `common_experiment.py`: shared experiment configuration.
- `common_eval.py`: common MEC evaluation runner.
- `compare_results.py`: comparison chart and final-summary generator.
- `baselines/`: additional baseline policies.
- `patches/`: local modifications applied to upstream DROO/QECO repositories for the shared evaluation pipeline.
- `experiment_results/comparisons/`: tracked comparison outputs used by the paper.
- `experiment_results/formula_visualizations/`: tracked formula figures referenced by the paper.
- `journals/README.md`: citation list for locally stored reference PDFs.

## Upstream Baseline Repositories

The upstream DROO and QECO repositories are cloned locally when running:

```bash
python3 QECO_DROO.py --execute clone droo
python3 QECO_DROO.py --execute clone qeco
```

After cloning, apply the shared-evaluation patches:

```bash
git -C DROO apply ../patches/droo-common-eval.patch
git -C QECO apply ../patches/qeco-common-eval.patch
```

These patches align the upstream baseline code with `common_experiment.py` and the current paper's shared MEC setting.

## Git Tracking Policy

The repository intentionally excludes:

- `env_droo/`, `env_qeco/`, and other virtual environments.
- `DROO/` and `QECO/` local clones, because they are upstream repositories with their own git histories.
- `journals/*.pdf`, because original papers may be licensed and should be cited by DOI instead of redistributed.
- raw `experiment_results/<algorithm>/run_*` folders, because they can be regenerated and grow quickly.

The tracked experiment artifacts are comparison summaries, comparison figures, and formula visualizations needed by the manuscript.

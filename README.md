# ML-Based Cloud Audit-Log Anomaly Detection (Month 1)

Local prototype that ranks unusual CloudTrail-style events for investigation using a rule-based baseline and an Isolation Forest. **An anomaly is not necessarily an attack.**

## Status
**Implemented (Month 1):** synthetic log generator, JSON/CSV ingestion, feature engineering, rule baseline, Isolation Forest, ranked CSV output, small test suite.
**Not implemented:** dashboard, AWS integration, plots, real-dataset evaluation (see Plan).

## Dataset (important)
No real public CloudTrail dataset was verified or downloaded for this submission. The project uses **synthetic data** generated locally. Ingestion also accepts raw CloudTrail JSON (`{"Records": [...]}`) or CSV, so a real dataset can be dropped into `data/raw/` later after checking its license.
Synthetic results reflect the generator's assumptions and **do not show real-world effectiveness**.

## Setup
Windows:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Linux/macOS:
```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Run
```
python scripts/generate_data.py
python scripts/run_detection.py --contamination 0.01
python -m pytest -q
```
Outputs: `results/scored_events.csv`, `results/metrics.csv`, `results/detector.joblib`.

## Structure
`src/` (data_generator, ingestion, preprocessing, baseline, detector), `scripts/`, `tests/`, `data/`, `results/`, `DATA_DICTIONARY.md`.

## Method
- **Features:** hour, day of week, error flag, per-user/IP event counts and per-user failures in 10-minute buckets, one-hot of event name, source, region, user.
- **Rules:** burst volume, repeated failures, privileged API, unexpected region. Each is configurable in `src/baseline.py` with its false-positive risk noted.
- **Isolation Forest:** random trees isolate points; shorter paths = more unusual. Score = negated `score_samples` (higher = more unusual). Flag threshold = top `contamination` fraction of training scores. Reasons shown are simple context checks, not native model explanations.
- **Evaluation:** train on first 70% of time, test on the last 30%. Labels used only for metrics.

## Actual results from one run (synthetic, seed 42, contamination 0.01)
| Detector | Flagged | Precision | Recall | F1 | FPR |
|---|---|---|---|---|---|
| Rule baseline | 191 | 0.984 | 1.000 | 0.992 | 0.0039 |
| Isolation Forest | 98 | 0.969 | 0.505 | 0.664 | 0.0039 |

The rules score high partly because the generator's scenarios were written to match them. Isolation Forest recall is limited by the 1% threshold and because several injected events resemble normal ones.

## Limitations
Synthetic data; anomalies injected only in the last 30% of time; 10-minute buckets use the whole file (not strictly causal); no real attack data; training data may contain anomalies.

## Plan (not done)
Month 2: more features/configs. Month 3: evaluation plots, Streamlit dashboard. Month 4: tests, architecture diagram, AWS S3/CloudTrail guidance, interview notes.

## Progress log
| Month | Planned | Status |
|---|---|---|
| 1 | Foundation | Done (see above) |
| 2 | Feature engineering | Not started |
| 3 | Evaluation + dashboard | Not started |
| 4 | Finalization | Not started |

## GitHub upload
```
git init
git add .
git commit -m "Month 1: audit-log anomaly detection prototype"
git branch -M main
git remote add origin https://github.com/<your-username>/cloud-audit-anomaly-detection.git
git push -u origin main
```
(Create the empty repo on github.com first.)

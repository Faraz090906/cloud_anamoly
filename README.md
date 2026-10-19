# ML-Based Cloud Audit-Log Anomaly Detection

A local machine learning prototype that analyzes CloudTrail-style audit events and ranks unusual activity for security investigation using a rule-based baseline and Isolation Forest.

**Important:** An anomaly is not necessarily an attack. This project prioritizes unusual events for review; it does not confirm security incidents.

## 1. Project Overview

Cloud environments generate audit logs that record actions performed by users, services, and applications. These logs can help security analysts investigate unusual API calls, repeated access failures, unexpected regional activity, and other potentially suspicious behavior.

This project explores how machine learning and interpretable rules can help identify unusual patterns in cloud audit events.

The initial implementation focuses on a local workflow using Python, pandas, NumPy, and scikit-learn. It does not require an AWS account, cloud deployment, or live credentials.

### Objectives

- Process structured audit events in JSON or CSV format.
- Extract useful numerical, temporal, and categorical features.
- Implement a simple rule-based detection baseline.
- Train an Isolation Forest model for unsupervised anomaly detection.
- Rank events by anomaly score and export the results.
- Compare the two detectors using labels available in the synthetic dataset.
- Build a foundation for future cloud security and visualization experiments.

### Project Scope

The project is designed as a four-month student project. This repository documents the initial Month 1 implementation rather than claiming that the entire roadmap has been completed.

## 2. Current Implementation Status

| Component | Status |
|---|---|
| Synthetic audit-log generator | Implemented |
| JSON and CSV ingestion | Implemented |
| Basic preprocessing and feature engineering | Implemented |
| Rule-based baseline | Implemented |
| Isolation Forest detector | Implemented |
| Ranked anomaly-score CSV output | Implemented |
| Evaluation metrics on synthetic data | Implemented |
| Small automated test suite | Implemented |
| Streamlit dashboard | Not implemented |
| Evaluation plots | Not implemented |
| Real-world CloudTrail dataset evaluation | Not implemented |
| Live AWS integration | Not implemented |

The implementation status above describes the project as reported for this Month 1 submission. Run the commands below to verify the current checkout and reproduce the results.

## 3. Dataset and Data Provenance

### Synthetic data

The current prototype uses **synthetic audit events generated locally**. No real public CloudTrail dataset was verified or downloaded for this submission.

The generator creates routine events and injected unusual activity. The generated labels are used to evaluate the detectors, not as input features for the unsupervised model.

This makes it possible to test the initial pipeline without exposing real security logs or requiring cloud access.

However, synthetic data has important limitations:

- The generator may produce simpler patterns than real cloud environments.
- The injected anomalies may closely match the rules used by the baseline.
- Real users can legitimately perform unusual actions.
- The synthetic distribution may not represent real attack behavior.
- Results depend on the generator's assumptions and scenario design.

Therefore, the reported metrics are **synthetic benchmark results only**. They do not establish that the detector can identify attacks in a real AWS environment.

### Input formats

The ingestion code supports:

- JSON event records.
- CloudTrail-style JSON objects containing a `Records` array.
- CSV files containing structured event columns.

A real dataset can be added later, after its source, license, data fields, and permitted use have been checked.

Do not upload private audit logs, credentials, account identifiers, or other sensitive information to a public repository.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| pandas | Event processing and tabular data manipulation |
| NumPy | Numerical operations |
| scikit-learn | Preprocessing and Isolation Forest |
| Isolation Forest | Unsupervised anomaly detection |
| pytest | Automated tests |
| joblib | Saving the fitted detector |
| Git and GitHub | Version control and project hosting |

The project is designed to run locally. AWS services and a dashboard are planned extensions, not requirements for the current implementation.

## 5. System Architecture

The Month 1 workflow is:

```text
             Audit Event Data
              JSON / CSV
                  |
                  v
        Data Ingestion and Parsing
                  |
                  v
          Preprocessing
   Missing Values / Time Parsing
                  |
                  v
          Feature Engineering
                  |
          +-------+-------+
          |               |
          v               v
    Rule-Based         Isolation
      Baseline           Forest
          |               |
          +-------+-------+
                  |
                  v
          Anomaly Ranking
                  |
                  v
       Scored Events and Metrics
                  |
                  v
          CSV / Model Outputs
```

The rule-based baseline and Isolation Forest provide two different ways to prioritize events.

The rule-based baseline checks explicit conditions. Isolation Forest identifies observations that appear unusual relative to the feature distribution learned during training.

Neither method independently confirms that an event represents malicious activity.

## 6. Repository Structure

The intended repository contains the following components:

```text
cloud-audit-anomaly-detection/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── data_generator.py
│   ├── ingestion.py
│   ├── preprocessing.py
│   ├── baseline.py
│   └── detector.py
├── scripts/
│   ├── generate_data.py
│   └── run_detection.py
├── tests/
├── results/
├── requirements.txt
├── .gitignore
├── DATA_DICTIONARY.md
└── README.md
```

This is a logical overview of the reported project structure. Keep the actual filenames consistent with the files in your repository; do not create empty files merely to match this example.

### Main modules

- `data_generator.py`: Generates synthetic audit events.
- `ingestion.py`: Loads JSON or CSV event data.
- `preprocessing.py`: Cleans data and constructs model features.
- `baseline.py`: Applies configurable rule-based checks.
- `detector.py`: Fits and applies Isolation Forest.
- `generate_data.py`: Runs the synthetic data-generation workflow.
- `run_detection.py`: Runs detection and writes the outputs.
- `tests/`: Contains automated tests for supported functionality.
- `DATA_DICTIONARY.md`: Documents fields, features, and assumptions.

## 7. Setup and Installation

### Prerequisites

Install Python and Git. Use a Python version supported by the dependencies in `requirements.txt`.

Check the installation:

```bash
python --version
git --version
```

On some Linux/macOS systems, use `python3` instead of `python`.

### Windows

Open a terminal in the project directory:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If package installation fails, check the Python version and the error message. Do not assume that installation succeeded until the command finishes without an error.

## 8. Running the Project

Run the following commands from the repository root.

### Step 1: Generate the synthetic dataset

```bash
python scripts/generate_data.py
```

This runs the project's local synthetic-data generator.

The exact output location and number of records depend on the implementation and its configuration. Check the terminal output and generated files to confirm where the data was written.

### Step 2: Run anomaly detection

```bash
python scripts/run_detection.py --contamination 0.01
```

The contamination parameter controls the approximate fraction of training observations that Isolation Forest treats as outliers when applying its fitted decision threshold.

A value of `0.01` corresponds to approximately 1% of the training observations being designated as outliers by that threshold. The number of events flagged in a separate test set may differ.

### Step 3: Run the tests

```bash
python -m pytest -q
```

Use the actual test output to confirm whether the tests passed.

### Expected output files

The current project description reports these outputs:

| File | Purpose |
|---|---|
| `results/scored_events.csv` | Events ranked with detector outputs |
| `results/metrics.csv` | Evaluation metrics |
| `results/detector.joblib` | Saved fitted detector |

Confirm the exact columns, serialization format, and output paths from the implementation. These outputs should be generated by running the project rather than manually creating example results.

## 9. Data Processing and Feature Engineering

The prototype uses features derived from event timestamps, event attributes, and aggregated activity.

### Time-based features

- Hour of day.
- Day of week.

These features can help represent periodic patterns in activity. For example, an event at an unusual hour may merit review, but unusual timing alone is not evidence of an attack.

### Event and identity features

- Event name.
- Event source.
- Region.
- User identity.
- Error or failure indicator.

Categorical features are converted into numerical representations suitable for the machine learning pipeline. The reported implementation uses one-hot encoding for event name, source, region, and user.

### Aggregated activity features

The prototype includes:

- Per-user event counts.
- Per-IP event counts.
- Per-user failures in 10-minute buckets.

These features can help identify bursts of activity and repeated failures that may be difficult to detect from an individual event alone.

**Implementation limitation:** The reported 10-minute aggregation uses the whole file rather than a strictly causal, event-by-event window. This can introduce temporal information leakage. It should be improved before drawing strong conclusions from time-sensitive evaluations.

### Missing values and duplicates

Missing fields should be handled explicitly rather than silently assuming that every event contains all CloudTrail attributes.

Duplicate handling must also be conservative: identical-looking events may represent legitimate repeated API activity.

Refer to `DATA_DICTIONARY.md` and the implementation for the exact field definitions and cleaning behavior.

## 10. Rule-Based Baseline

The rule-based baseline uses explicit conditions to flag potentially unusual events.

The reported rules cover:

- High event volume or burst activity.
- Repeated failures.
- Privileged API activity.
- Unexpected region activity.

Each rule has a different false-positive risk.

For example, a burst of API calls may result from a legitimate automated workload, and a privileged API call may be part of normal administrative work.

Unexpected-region detection also depends on having a reliable baseline for expected regions. A region that is unfamiliar to the detector is not necessarily unauthorized.

The baseline is valuable because its behavior is easy to inspect. It also provides a comparison point for the machine learning model.

The precise conditions and thresholds should be documented in `src/baseline.py`.

## 11. Isolation Forest

Isolation Forest is an unsupervised anomaly-detection algorithm that isolates observations using randomly selected features and split points.

The underlying intuition is that unusual observations are often easier to isolate than observations within dense, common patterns.

### How it works

1. Randomized trees are built using subsets of the data.
2. Each observation is passed through the trees.
3. Observations that are isolated using shorter paths tend to be more anomalous.
4. The model assigns scores that can be used to rank observations.

In the reported implementation, the anomaly ranking score is the negated scikit-learn `score_samples` output. Under this convention, **higher scores indicate more unusual observations**.

The `contamination` parameter influences the threshold used to designate observations as outliers. It should not be interpreted as the true prevalence of attacks in a real environment.

### Interpreting alerts

An Isolation Forest score measures unusualness relative to the data and features used by the model. It is not a probability that an event is malicious.

For flagged events, the project provides simple contextual checks as reasons for review. These are not native causal explanations of the model's prediction.

A reviewer should inspect the original event and relevant context before deciding whether any action is necessary.

## 12. Evaluation Methodology

The reported evaluation uses a chronological split:

- First 70% of the events by time: training.
- Final 30%: testing.

Synthetic labels are used for evaluation metrics and are not intended to be model input features.

This is preferable to randomly splitting events when chronological behavior matters, but it does not eliminate all evaluation issues.

### Important limitations

- Injected anomalies occur only in the final 30% of the generated timeline.
- Some synthetic scenarios directly match the baseline rules.
- The aggregation features use the full file rather than a strictly causal window.
- Training data may contain anomalies.
- Synthetic scenarios may not represent real cloud security incidents.

These limitations affect how the results should be interpreted.

### Reported results

The following values were supplied for one synthetic run with seed `42` and contamination `0.01`. They are reported here as provided; they have not been independently reproduced by this README.

| Detector | Flagged | Precision | Recall | F1 | False-positive rate |
|---|---:|---:|---:|---:|---:|
| Rule-based baseline | 191 | 0.984 | 1.000 | 0.992 | 0.0039 |
| Isolation Forest | 98 | 0.969 | 0.505 | 0.664 | 0.0039 |

These results are **not evidence of real-world attack detection effectiveness**.

The baseline's high scores are partly explained by the fact that the synthetic scenarios were designed to match its rules. Isolation Forest's recall is limited by the selected threshold and by injected events that resemble routine activity.

Before publishing these numbers as verified results, rerun the experiment and check the output in `results/metrics.csv`.

### Understanding the metrics

- **Precision:** The fraction of flagged events that are labeled anomalous.
- **Recall:** The fraction of labeled anomalous events that are flagged.
- **F1 score:** The harmonic mean of precision and recall.
- **False-positive rate:** The fraction of normal events incorrectly flagged.

For security monitoring, a high false-positive rate can overwhelm reviewers. Conversely, a low false-positive rate does not guarantee that the detector finds enough suspicious events.

Metrics should be interpreted alongside alert volume, missed anomalies, the data-generation process, and the consequences of different errors.

## 13. Testing

The project includes a small test suite.

Run it using:

```bash
python -m pytest -q
```

Useful areas to test include:

- Loading supported JSON and CSV structures.
- Handling missing or malformed fields.
- Constructing features with expected columns.
- Producing valid scores and ranked events.
- Preserving event records through preprocessing.
- Running the detector on a small valid dataset.

Only describe a test as passing when it has actually been run successfully. Extend the tests as the project develops.

## 14. Limitations and Security Considerations

The current version is a local learning prototype, not a production security monitoring service.

Its limitations include:

1. **Synthetic data:** The data may not represent real cloud behavior or attacks.
2. **Rule dependence:** The baseline benefits from scenarios intentionally designed to trigger its rules.
3. **Threshold sensitivity:** Changing the contamination parameter changes the alerting behavior.
4. **Temporal leakage:** Whole-file aggregation can use information that would not have been available at the time of an event.
5. **Incomplete context:** An event's risk depends on identity, permissions, resource, and surrounding activity.
6. **No incident confirmation:** Anomaly scores cannot establish malicious intent.
7. **No live AWS integration:** The current implementation does not demonstrate collection or analysis of live AWS logs.

If real logs are used later, protect sensitive information, avoid committing raw logs to public repositories, and follow the dataset owner's usage terms.

## 15. Four-Month Development Plan

Only Month 1 is represented as implemented in this submission.

| Month | Planned work | Status |
|---|---|---|
| Month 1 | Data generation and ingestion, preprocessing, baseline, Isolation Forest, ranked output | Reported complete |
| Month 2 | Improve time-based and user-activity features; compare a small number of feature configurations | Not started |
| Month 3 | Improve evaluation, add plots, build a basic Streamlit dashboard and event-level explanations | Not started |
| Month 4 | Fix bugs, improve tests, finalize documentation and architecture diagram, prepare interview notes, document optional AWS integration | Not started |

The timeline should be updated as work is actually completed. Planned tasks should not be described as implemented features.

## 16. Optional AWS Extension

AWS integration is outside the Month 1 implementation.

A future version could analyze CloudTrail logs exported to Amazon S3:

- **AWS CloudTrail:** Records supported AWS account activity.
- **Amazon S3:** Stores exported log files.
- **IAM:** Controls access to the relevant resources.
- **Python and scikit-learn:** Process events and calculate anomaly scores.
- **CloudWatch or a suitable notification service:** Could support optional monitoring and alert delivery.

Any later integration should use least-privilege permissions and secure credential handling. It should be implemented and tested before being described as a working integration.

## 17. How to Upload the Project to GitHub

### Step 1: Create a repository

1. Open GitHub.
2. Create a new repository named `cloud-audit-anomaly-detection`.
3. Choose whether the repository should be public or private.
4. Avoid initializing it with a README if you already have a local project containing one.

### Step 2: Check `.gitignore`

Make sure generated caches, virtual environments, local credentials, and sensitive data are excluded. For example:

```gitignore
venv/
.venv/
__pycache__/
.pytest_cache/
*.py[cod]
.env
.DS_Store
```

Add project-specific exclusions for private logs and generated files as needed. Do not exclude source code or documentation that should be tracked.

### Step 3: Initialize Git and commit

From the project root:

```bash
git init
git add .
git status
git commit -m "Month 1: audit-log anomaly detection prototype"
git branch -M main
```

Review `git status` before committing to ensure that private logs, credentials, and unwanted generated files are not staged.

### Step 4: Connect the remote repository

Replace `<your-username>` with your GitHub username:

```bash
git remote add origin https://github.com/<your-username>/cloud-audit-anomaly-detection.git
git push -u origin main
```

If a remote named `origin` already exists, inspect it with `git remote -v` rather than adding a duplicate.

### Step 5: Verify the repository

Open the GitHub repository and check that:

- `README.md` renders correctly.
- The source files and tests are present.
- The setup and run commands are accurate.
- No credentials or sensitive logs were uploaded.
- Reported results match actual experiment outputs.

## 18. Future Improvements

After the Month 1 pipeline is reproducible, possible improvements include:

- Strictly causal rolling-window features.
- Better time-based evaluation.
- Comparisons across a small number of feature configurations.
- Evaluation plots and threshold analysis.
- A Streamlit interface for investigating flagged events.
- Testing against a suitable, licensed real-world dataset.
- Optional AWS integration guidance.

These improvements should be added incrementally. The priority is to maintain a working, understandable, and reproducible project rather than increasing complexity for its own sake.

## 19. Learning Outcomes

This project provides practice with:

- Structured data ingestion and cleaning.
- Feature engineering using pandas and NumPy.
- Categorical preprocessing.
- Unsupervised anomaly detection with scikit-learn.
- Rule-based versus machine learning comparisons.
- Precision, recall, F1, and false-positive rate.
- Reproducibility, testing, and version control.
- Basic cloud audit-log and security concepts.

The central lesson is that anomaly detection is a ranking and investigation aid, not a substitute for security analysis.

---

**Project status:** Month 1 prototype, using synthetic data. Real-world effectiveness and live AWS integration have not been established.
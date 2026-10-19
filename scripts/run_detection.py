"""Run baseline + Isolation Forest. Train on first 70% of time, test on the rest."""
import argparse, sys
from pathlib import Path
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ingestion import load_events
from src.preprocessing import add_features
from src.baseline import apply_rules
from src.detector import AnomalyDetector


def metrics(y_true, y_pred, name):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
    return {"detector": name, "flagged": int(y_pred.sum()), "precision": p, "recall": r,
            "f1": f, "fpr": fp / max(fp + tn, 1), "tp": tp, "fp": fp, "fn": fn, "tn": tn}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default="data/processed/synthetic_events.json")
    ap.add_argument("--labels", default="data/processed/synthetic_labels.csv",
                    help="Used ONLY for evaluation. Pass '' to skip.")
    ap.add_argument("--contamination", type=float, default=0.01)
    args = ap.parse_args()

    df, dropped = load_events(args.events)
    print(f"Loaded {len(df)} events ({dropped} malformed dropped)")
    feats = add_features(df)
    cut = feats["eventTime"].quantile(0.7)
    train, test = feats[feats["eventTime"] <= cut], feats[feats["eventTime"] > cut]

    det = AnomalyDetector(contamination=args.contamination).fit(train)
    ranked = apply_rules(det.rank(test))
    Path("results").mkdir(exist_ok=True)
    det.save("results/detector.joblib")

    if args.labels and Path(args.labels).exists():
        labels = pd.read_csv(args.labels)
        ranked = ranked.merge(labels, on="eventID", how="left")
        y = ranked["is_anomaly"].fillna(0).astype(int)
        res = pd.DataFrame([metrics(y, ranked["baseline_flag"], "rule_baseline"),
                            metrics(y, ranked["ml_flag"], "isolation_forest")])
        res.to_csv("results/metrics.csv", index=False)
        print(res.to_string(index=False))
        print("NOTE: metrics are on SYNTHETIC data and reflect generator assumptions only.")

    ranked.to_csv("results/scored_events.csv", index=False)
    print("Saved results/scored_events.csv and results/detector.joblib")
    print(ranked[["eventTime", "userName", "eventName", "anomaly_score", "ml_reasons"]].head(10).to_string())


if __name__ == "__main__":
    main()

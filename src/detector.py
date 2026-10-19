"""Isolation Forest detector.

Isolation Forest builds random trees that split features at random values.
Points that need few splits to isolate are unusual relative to training data.
Unusual does not mean malicious.
"""
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from .preprocessing import build_preprocessor


class AnomalyDetector:
    def __init__(self, contamination=0.01, n_estimators=200, random_state=42):
        self.contamination = contamination
        self.pipeline = Pipeline([
            ("prep", build_preprocessor()),
            ("model", IsolationForest(n_estimators=n_estimators, contamination=contamination,
                                      random_state=random_state)),
        ])
        self.threshold_ = None
        self.stats_ = {}

    def fit(self, features_df):
        """Fit on engineered features only (no labels)."""
        self.pipeline.fit(features_df)
        scores = self.score(features_df)
        self.threshold_ = float(np.quantile(scores, 1 - self.contamination))
        self.stats_ = {
            "event_freq": features_df["eventName"].value_counts(normalize=True).to_dict(),
            "region_freq": features_df["awsRegion"].value_counts(normalize=True).to_dict(),
            "events_p99": float(features_df["user_events_10min"].quantile(0.99)),
        }
        return self

    def score(self, features_df):
        """Higher = more unusual."""
        return -self.pipeline.score_samples(features_df)

    def rank(self, features_df, threshold=None):
        out = features_df.copy()
        out["anomaly_score"] = self.score(features_df)
        thr = self.threshold_ if threshold is None else threshold
        out["ml_flag"] = (out["anomaly_score"] >= thr).astype(int)
        out["ml_reasons"] = self.explain(out)
        return out.sort_values("anomaly_score", ascending=False).reset_index(drop=True)

    def explain(self, df):
        """Transparent context checks (not native Isolation Forest explanations)."""
        reasons = []
        for _, r in df.iterrows():
            why = []
            if r["is_error"]:
                why.append(f"failed API call ({r['errorCode']})")
            if r["user_events_10min"] > self.stats_["events_p99"]:
                why.append(f"high user volume ({int(r['user_events_10min'])} events/10min)")
            if self.stats_["event_freq"].get(r["eventName"], 0) < 0.005:
                why.append("rare event name in training data")
            if self.stats_["region_freq"].get(r["awsRegion"], 0) < 0.02:
                why.append("rare region in training data")
            reasons.append("; ".join(why))
        return reasons

    def save(self, path):
        joblib.dump(self, path)

    @staticmethod
    def load(path):
        return joblib.load(path)

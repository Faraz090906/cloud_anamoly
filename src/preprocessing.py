"""Feature engineering + scikit-learn preprocessing."""
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CATEGORICAL = ["eventName", "eventSource", "awsRegion", "userName"]
NUMERIC = ["hour", "day_of_week", "is_error", "user_events_10min",
           "user_failures_10min", "ip_events_10min"]


def add_features(df):
    """Add simple features. Labels are never used here.

    The 10-minute counts use fixed time buckets (not strictly causal);
    acceptable for a prototype and documented in the README.
    """
    out = df.copy()
    out["hour"] = out["eventTime"].dt.hour
    out["day_of_week"] = out["eventTime"].dt.dayofweek
    out["is_error"] = out["errorCode"].notna().astype(int)
    out["bucket"] = out["eventTime"].dt.floor("10min")
    out["user_events_10min"] = out.groupby(["userName", "bucket"])["eventName"].transform("size")
    out["user_failures_10min"] = out.groupby(["userName", "bucket"])["is_error"].transform("sum")
    out["ip_events_10min"] = out.groupby(["sourceIPAddress", "bucket"])["eventName"].transform("size")
    return out.drop(columns=["bucket"])


def build_preprocessor():
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5, sparse_output=False), CATEGORICAL),
        ("num", StandardScaler(), NUMERIC),
    ])

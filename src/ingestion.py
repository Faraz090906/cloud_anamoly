"""Load and normalize audit logs from JSON or CSV."""
import json
from pathlib import Path
import pandas as pd

REQUIRED = ["eventTime", "eventName"]
OPTIONAL = ["eventSource", "userName", "sourceIPAddress", "awsRegion",
            "userAgent", "errorCode", "eventID"]


def _flatten_record(rec):
    """Support raw CloudTrail records (nested userIdentity) and flat ones."""
    rec = dict(rec)
    ident = rec.get("userIdentity")
    if isinstance(ident, dict) and "userName" not in rec:
        rec["userName"] = ident.get("userName") or ident.get("arn") or ident.get("type")
    return rec


def load_events(path):
    """Return (clean_df, n_dropped)."""
    path = Path(path)
    if path.suffix.lower() == ".json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("Records", []) if isinstance(data, dict) else data
        df = pd.DataFrame([_flatten_record(r) for r in records if isinstance(r, dict)])
    elif path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    return normalize(df)


def normalize(df):
    """Drop malformed rows; keep legitimate repeats (dedupe only by identical eventID)."""
    n_start = len(df)
    for col in REQUIRED:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    df = df.copy()
    for col in OPTIONAL:
        if col not in df.columns:
            df[col] = None
    df["eventTime"] = pd.to_datetime(df["eventTime"], errors="coerce", utc=True)
    df = df.dropna(subset=["eventTime", "eventName"])
    has_id = df["eventID"].notna()
    if has_id.any():
        df = pd.concat([df[has_id].drop_duplicates("eventID"), df[~has_id]])
    for col in ["eventSource", "userName", "awsRegion", "userAgent", "sourceIPAddress"]:
        df[col] = df[col].fillna("unknown").astype(str)
    df["errorCode"] = df["errorCode"].astype(object).where(df["errorCode"].notna(), None)
    df = df.sort_values("eventTime").reset_index(drop=True)
    return df, n_start - len(df)

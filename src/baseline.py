"""Rule-based baseline. Each rule is configurable; false-positive risks are noted."""
import pandas as pd

DEFAULT_CONFIG = {
    "max_events_10min": 40,       # FP: legitimate batch jobs/scripts
    "max_failures_10min": 5,      # FP: expired credentials, misconfigured apps
    "privileged_events": ["CreateAccessKey", "AttachUserPolicy", "PutUserPolicy", "CreateUser",
                          "StopLogging", "DeleteTrail", "PutBucketPolicy"],  # FP: normal admin work
    "expected_regions": ["us-east-1", "us-west-2"],  # FP: travel, new regional deployments
}


def apply_rules(df, config=None):
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    out = df.copy()
    flags = {
        "burst_volume": out["user_events_10min"] > cfg["max_events_10min"],
        "repeated_failures": out["user_failures_10min"] >= cfg["max_failures_10min"],
        "privileged_api": out["eventName"].isin(cfg["privileged_events"]),
        "unexpected_region": ~out["awsRegion"].isin(cfg["expected_regions"]),
    }
    for name, series in flags.items():
        out[f"rule_{name}"] = series.astype(int)
    out["baseline_flag"] = pd.concat(flags, axis=1).any(axis=1).astype(int)
    out["baseline_reasons"] = [
        "; ".join(n for n in flags if flags[n].iloc[i]) for i in range(len(out))
    ]
    return out

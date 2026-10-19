"""Synthetic CloudTrail-style log generator (SYNTHETIC DATA ONLY).

Events and ground-truth labels are returned separately so labels can never
leak into model features.
"""
import numpy as np
import pandas as pd

USERS = [f"user{i:02d}" for i in range(1, 13)]
HOME_REGIONS = ["us-east-1", "us-west-2"]
UNUSUAL_REGIONS = ["ap-southeast-1", "eu-north-1"]
ROUTINE_EVENTS = [
    ("s3.amazonaws.com", "GetObject", 0.30),
    ("s3.amazonaws.com", "ListBuckets", 0.08),
    ("s3.amazonaws.com", "PutObject", 0.12),
    ("ec2.amazonaws.com", "DescribeInstances", 0.15),
    ("iam.amazonaws.com", "GetUser", 0.05),
    ("lambda.amazonaws.com", "ListFunctions", 0.08),
    ("logs.amazonaws.com", "DescribeLogGroups", 0.07),
    ("sts.amazonaws.com", "GetCallerIdentity", 0.15),
]
USER_AGENTS = ["aws-cli/2.15", "Boto3/1.34", "console.amazonaws.com"]


def _event(rng, ts, user, ip, region, source, name, agent, error=None):
    return {
        "eventTime": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "eventSource": source,
        "eventName": name,
        "userName": user,
        "sourceIPAddress": ip,
        "awsRegion": region,
        "userAgent": agent,
        "errorCode": error,
        "eventID": f"{int(rng.integers(0, 2**62)):016x}",
    }


def generate_synthetic_logs(n_routine=3000, days=7, seed=42):
    """Return (events_df, labels_df). Anomalies are injected in the last 30% of time."""
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2024-01-01T00:00:00Z")
    home_ip = {u: f"10.0.{i}.{int(rng.integers(2, 250))}" for i, u in enumerate(USERS)}
    user_agent = {u: USER_AGENTS[i % len(USER_AGENTS)] for i, u in enumerate(USERS)}
    srcs, names, probs = zip(*ROUTINE_EVENTS)
    probs = np.array(probs) / sum(probs)
    rows, labels = [], []

    def add(ev, scenario):
        rows.append(ev)
        labels.append({"eventID": ev["eventID"], "is_anomaly": int(scenario != "routine"),
                       "scenario": scenario})

    for _ in range(n_routine):
        day = int(rng.integers(0, days))
        hour = int(np.clip(rng.normal(13, 3), 0, 23))
        ts = start + pd.Timedelta(days=day, hours=hour,
                                  minutes=int(rng.integers(0, 60)), seconds=int(rng.integers(0, 60)))
        u = USERS[int(rng.integers(0, len(USERS)))]
        k = int(rng.choice(len(names), p=probs))
        err = "AccessDenied" if rng.random() < 0.02 else None
        add(_event(rng, ts, u, home_ip[u], HOME_REGIONS[int(rng.integers(0, 2))],
                   srcs[k], names[k], user_agent[u], err), "routine")

    def late_time():
        return start + pd.Timedelta(days=int(rng.integers(int(days * 0.7) + 1, days)),
                                    hours=int(rng.integers(0, 24)), minutes=int(rng.integers(0, 50)))

    def pick_user():
        return USERS[int(rng.integers(0, len(USERS)))]

    for _ in range(2):  # 1. burst
        u, t0 = pick_user(), late_time()
        for j in range(80):
            add(_event(rng, t0 + pd.Timedelta(seconds=int(j * 1.5)), u, home_ip[u], "us-east-1",
                       "ec2.amazonaws.com", "DescribeInstances", user_agent[u]), "burst")
    for _ in range(2):  # 2. repeated failures
        u, t0 = pick_user(), late_time()
        for j in range(15):
            add(_event(rng, t0 + pd.Timedelta(seconds=20 * j), u, home_ip[u], "us-east-1",
                       "s3.amazonaws.com", "GetObject", user_agent[u], "AccessDenied"),
                "repeated_failures")
    for _ in range(3):  # 3. unusual region + new IP
        u, t0 = pick_user(), late_time()
        for j in range(4):
            add(_event(rng, t0 + pd.Timedelta(minutes=j), u, f"203.0.113.{int(rng.integers(2, 250))}",
                       UNUSUAL_REGIONS[int(rng.integers(0, 2))], "ec2.amazonaws.com",
                       "DescribeInstances", "aws-cli/2.15"), "unusual_region")
    for name in ["CreateAccessKey", "AttachUserPolicy", "PutUserPolicy", "CreateUser"]:  # 4. privilege
        u, t0 = pick_user(), late_time()
        add(_event(rng, t0, u, home_ip[u], "us-east-1", "iam.amazonaws.com", name, user_agent[u]),
            "privilege_activity")
    for name in ["StopLogging", "DeleteTrail", "PutBucketPolicy"]:  # 5. unfamiliar events
        u, t0 = pick_user(), late_time()
        src = "s3.amazonaws.com" if name == "PutBucketPolicy" else "cloudtrail.amazonaws.com"
        add(_event(rng, t0, u, home_ip[u], "us-east-1", src, name, user_agent[u]), "unfamiliar_event")

    events = pd.DataFrame(rows).sort_values("eventTime").reset_index(drop=True)
    return events, pd.DataFrame(labels)

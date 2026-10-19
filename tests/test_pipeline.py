import json
from src.data_generator import generate_synthetic_logs
from src.ingestion import load_events, normalize
from src.preprocessing import add_features, NUMERIC
from src.baseline import apply_rules
from src.detector import AnomalyDetector


def test_generator_is_reproducible_and_labels_separate():
    a, la = generate_synthetic_logs(n_routine=200, seed=1)
    b, _ = generate_synthetic_logs(n_routine=200, seed=1)
    assert a.equals(b)
    assert "is_anomaly" not in a.columns and la["is_anomaly"].sum() > 0


def test_ingestion_drops_malformed_keeps_repeats(tmp_path):
    recs = [{"eventTime": "2024-01-01T00:00:00Z", "eventName": "A"},
            {"eventTime": "2024-01-01T00:00:00Z", "eventName": "A"},
            {"eventTime": "not-a-date", "eventName": "B"}]
    p = tmp_path / "x.json"
    p.write_text(json.dumps(recs))
    df, dropped = load_events(p)
    assert len(df) == 2 and dropped == 1


def test_features_and_baseline():
    ev, _ = generate_synthetic_logs(n_routine=300, seed=2)
    f = add_features(normalize(ev)[0])
    assert all(c in f.columns for c in NUMERIC)
    assert "baseline_flag" in apply_rules(f).columns


def test_detector_fit_rank_save_load(tmp_path):
    ev, _ = generate_synthetic_logs(n_routine=500, seed=3)
    f = add_features(normalize(ev)[0])
    det = AnomalyDetector(contamination=0.02).fit(f)
    ranked = det.rank(f)
    assert ranked["anomaly_score"].is_monotonic_decreasing
    det.save(tmp_path / "d.joblib")
    assert len(AnomalyDetector.load(tmp_path / "d.joblib").score(f)) == len(f)

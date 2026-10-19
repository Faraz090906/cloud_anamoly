"""Generate SYNTHETIC logs. Labels are written to a separate file."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_generator import generate_synthetic_logs

events, labels = generate_synthetic_logs()
out = Path("data/processed"); out.mkdir(parents=True, exist_ok=True)
(out / "synthetic_events.json").write_text(json.dumps(events.to_dict(orient="records"), indent=1))
labels.to_csv(out / "synthetic_labels.csv", index=False)
print(f"Wrote {len(events)} SYNTHETIC events and labels to {out}")

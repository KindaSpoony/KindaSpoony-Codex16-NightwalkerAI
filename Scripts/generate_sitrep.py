import json
import datetime
from pathlib import Path

SITREP_PATH = Path("../SITREPs")
LOG_PATH = Path("../Logs")

def generate_sitrep():
    drift_files = sorted(LOG_PATH.glob("drift_*.json"), reverse=True)
    latest_drift = json.loads(drift_files[0].read_text()) if drift_files else []

    sitrep = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "runner_id": "vaultis-runner-001",
        "fleet_id": "vaultis-fleet-alpha",
        "recent_drift_events": latest_drift,
        "status": "operational",
        "notes": "Auto-generated SITREP from VAULTIS Runner"
    }

    sitrep_file = SITREP_PATH / f"SITREP_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.md"
    with open(sitrep_file, 'w') as f:
        f.write(f"# SITREP - {sitrep['timestamp']}\n\n")
        f.write(json.dumps(sitrep, indent=2))

if __name__ == "__main__":
    generate_sitrep()

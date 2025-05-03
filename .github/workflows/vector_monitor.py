import yaml
import json
import logging
import hashlib
from pathlib import Path
import datetime

logging.basicConfig(level=logging.INFO)

CODEX_PATH = Path("../Codex16")
LOG_PATH = Path("../Logs")

def calculate_file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def check_drift():
    drift_log = []
    for yaml_file in CODEX_PATH.glob("*.yaml"):
        current_hash = calculate_file_hash(yaml_file)
        hash_record_file = LOG_PATH / f"{yaml_file.stem}_hash.json"
        
        if hash_record_file.exists():
            previous_hash = json.loads(hash_record_file.read_text())["hash"]
            if previous_hash != current_hash:
                drift_entry = {
                    "file": yaml_file.name,
                    "previous_hash": previous_hash,
                    "current_hash": current_hash,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
                drift_log.append(drift_entry)
                logging.warning(f"Drift detected in {yaml_file.name}")
        else:
            logging.info(f"No previous record found for {yaml_file.name}. Creating one.")

        hash_record_file.write_text(json.dumps({"hash": current_hash}, indent=2))

    if drift_log:
        drift_log_file = LOG_PATH / f"drift_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
        drift_log_file.write_text(json.dumps(drift_log, indent=2))
        logging.info(f"Drift log updated: {drift_log_file.name}")

if __name__ == "__main__":
    check_drift()

import yaml
import json
import logging
import hashlib
from pathlib import Path
import datetime
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("vector_monitor")

# Load configuration
def load_config():
    try:
        config_path = Path("runner_config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        else:
            logger.warning("Configuration file not found, using defaults")
            return {"codex_source": "Codex16"}
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {"codex_source": "Codex16"}

config = load_config()
CODEX_PATH = Path(config.get("codex_source", "Codex16"))
LOG_PATH = Path("Logs")

def ensure_directories():
    """Ensure required directories exist"""
    for path in [CODEX_PATH, LOG_PATH]:
        if not path.exists():
            logger.info(f"Creating directory: {path}")
            path.mkdir(parents=True, exist_ok=True)

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {filepath}: {e}")
        return None

def check_drift():
    """Check for drift in YAML files in the Codex directory"""
    ensure_directories()
    drift_log = []

    yaml_files = list(CODEX_PATH.glob("*.yaml")) + list(CODEX_PATH.glob("*.yml"))
    if not yaml_files:
        logger.warning(f"No YAML files found in {CODEX_PATH}")
        return

    for yaml_file in yaml_files:
        current_hash = calculate_file_hash(yaml_file)
        if not current_hash:
            continue

        hash_record_file = LOG_PATH / f"{yaml_file.stem}_hash.json"

        if hash_record_file.exists():
            try:
                previous_hash = json.loads(hash_record_file.read_text())["hash"]
                if previous_hash != current_hash:
                    drift_entry = {
                        "file": yaml_file.name,
                        "previous_hash": previous_hash,
                        "current_hash": current_hash,
                        "timestamp": datetime.datetime.utcnow().isoformat()
                    }
                    drift_log.append(drift_entry)
                    logger.warning(f"Drift detected in {yaml_file.name}")
            except Exception as e:
                logger.error(f"Error reading previous hash for {yaml_file.name}: {e}")
        else:
            logger.info(f"No previous record found for {yaml_file.name}. Creating one.")

        # Update hash record
        try:
            hash_record_file.write_text(json.dumps({"hash": current_hash}, indent=2))
        except Exception as e:
            logger.error(f"Error writing hash record for {yaml_file.name}: {e}")

    if drift_log:
        timestamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        drift_log_file = LOG_PATH / f"drift_{timestamp}.json"
        try:
            drift_log_file.write_text(json.dumps(drift_log, indent=2))
            logger.info(f"Drift log updated: {drift_log_file.name}")
        except Exception as e:
            logger.error(f"Error writing drift log: {e}")

if __name__ == "__main__":
    logger.info("Starting vector drift monitor")
    check_drift()
    logger.info("Vector drift monitoring complete")
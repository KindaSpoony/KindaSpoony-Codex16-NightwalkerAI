import json
import datetime
from pathlib import Path
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("sitrep_generator")

# Use absolute paths
SITREP_PATH = Path("SITREPs")
LOG_PATH = Path("Logs")

def ensure_directories():
    """Ensure required directories exist"""
    for path in [SITREP_PATH, LOG_PATH]:
        if not path.exists():
            logger.info(f"Creating directory: {path}")
            path.mkdir(parents=True, exist_ok=True)

def generate_sitrep():
    """Generate a situation report based on recent drift events"""
    ensure_directories()

    drift_files = sorted(LOG_PATH.glob("drift_*.json"), reverse=True)

    # Handle case where no drift files exist
    if drift_files:
        try:
            latest_drift = json.loads(drift_files[0].read_text())
            logger.info(f"Found latest drift log: {drift_files[0].name}")
        except Exception as e:
            logger.error(f"Error reading drift file {drift_files[0]}: {e}")
            latest_drift = []
    else:
        logger.warning("No drift log files found")
        latest_drift = []

    # Generate SITREP data
    sitrep = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "runner_id": "vaultis-runner-001",
        "fleet_id": "vaultis-fleet-alpha",
        "recent_drift_events": latest_drift,
        "status": "operational",
        "notes": "Auto-generated SITREP from VAULTIS Runner"
    }

    # Generate detailed Markdown report
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    sitrep_file = SITREP_PATH / f"SITREP_{timestamp}.md"

    try:
        with open(sitrep_file, 'w') as f:
            f.write(f"# SITREP - {sitrep['timestamp']}\n\n")
            f.write(f"## Runner Information\n")
            f.write(f"- **Runner ID:** {sitrep['runner_id']}\n")
            f.write(f"- **Fleet ID:** {sitrep['fleet_id']}\n")
            f.write(f"- **Status:** {sitrep['status']}\n")
            f.write(f"- **Generated:** {sitrep['timestamp']}\n\n")

            f.write(f"## Recent Drift Events\n")
            if latest_drift:
                for event in latest_drift:
                    f.write(f"- **File:** {event['file']}\n")
                    f.write(f"  - Previous Hash: `{event['previous_hash'][:8]}...`\n")
                    f.write(f"  - Current Hash: `{event['current_hash'][:8]}...`\n")
                    f.write(f"  - Timestamp: {event['timestamp']}\n\n")
            else:
                f.write("No drift events detected in the monitoring period.\n\n")

            f.write(f"## Notes\n")
            f.write(f"{sitrep['notes']}\n")

        logger.info(f"SITREP generated: {sitrep_file}")
    except Exception as e:
        logger.error(f"Error writing SITREP file: {e}")

    # Also save JSON version for programmatic access
    try:
        sitrep_json = SITREP_PATH / f"SITREP_{timestamp}.json"
        with open(sitrep_json, 'w') as f:
            json.dump(sitrep, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing SITREP JSON file: {e}")

if __name__ == "__main__":
    logger.info("Generating SITREP")
    generate_sitrep()
    logger.info("SITREP generation complete")import json
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

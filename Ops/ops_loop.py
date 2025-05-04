import schedule
import time
import subprocess
import logging
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ops_loop")

def ensure_script_paths():
    """Verify script paths exist, return True if both exist"""
    scripts_dir = Path("Scripts")
    vector_monitor = scripts_dir / "vector_monitor.py"
    generate_sitrep = scripts_dir / "generate_sitrep.py"

    # Check if scripts exist
    if not vector_monitor.exists():
        logger.error(f"Vector monitor script not found at {vector_monitor}")
        return False

    if not generate_sitrep.exists():
        logger.error(f"SITREP generator script not found at {generate_sitrep}")
        return False

    return True

def run_drift_monitor():
    """Run the drift monitor and SITREP generator"""
    logger.info("Running drift monitor and SITREP...")

    if not ensure_script_paths():
        logger.error("Script paths verification failed. Aborting run.")
        return

    try:
        # Run vector monitor
        logger.info("Starting vector monitor")
        result = subprocess.run(["python", "Scripts/vector_monitor.py"],
                                  capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(f"Vector monitor failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
        else:
            logger.info("Vector monitor completed successfully")

        # Run SITREP generator
        logger.info("Starting SITREP generator")
        result = subprocess.run(["python", "Scripts/generate_sitrep.py"],
                                  capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(f"SITREP generator failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
        else:
            logger.info("SITREP generator completed successfully")

    except Exception as e:
        logger.error(f"Error during operations loop: {e}")

# Set up scheduling
def initialize_schedule():
    """Initialize the operations schedule"""
    # Run every 2 hours
    schedule.every(2).hours.do(run_drift_monitor)

    # Also run once at startup
    logger.info("Running initial drift monitor and SITREP...")
    run_drift_monitor()

    logger.info("VAULTIS Ops loop initialized with 2-hour schedule")

if __name__ == "__main__":
    logger.info("Starting VAULTIS Operations Loop")
    initialize_schedule()

    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Operations loop terminated by user")
    except Exception as e:
        logger.error(f"Operations loop crashed: {e}")

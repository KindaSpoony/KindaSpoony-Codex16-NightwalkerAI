import schedule
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

def run_drift_monitor():
    logging.info("Running drift monitor and SITREP...")
    subprocess.run(["python", "../Scripts/vector_monitor.py"])
    subprocess.run(["python", "../Scripts/generate_sitrep.py"])

# Run every 2 hours
schedule.every(2).hours.do(run_drift_monitor)

logging.info("VAULTIS Ops loop initialized...")

while True:
    schedule.run_pending()
    time.sleep(60)

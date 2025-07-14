#!/usr/bin/env python3
import subprocess
import os
import argparse
import logging
from datetime import datetime

# === Argument Parser ===
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--downloads', required=True, help='Path to downloads directory (containing datasets)')
    return parser.parse_args()

# === Logging Setup ===
os.makedirs("logs", exist_ok=True)

logfile = "logs/uploads.log"
success_logfile = "logs/upload_success.log"
failure_logfile = "logs/upload_failure.log"
tracker_file = "datasets_uploaded.txt"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(logfile, mode='a'),
        logging.StreamHandler()
    ]
)

success_logger = logging.getLogger("success")
success_logger.setLevel(logging.INFO)
success_handler = logging.FileHandler(success_logfile, mode='a')
success_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
success_logger.addHandler(success_handler)

failure_logger = logging.getLogger("failure")
failure_logger.setLevel(logging.INFO)
failure_handler = logging.FileHandler(failure_logfile, mode='a')
failure_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
failure_logger.addHandler(failure_handler)

# === Read shortnames file ===
def read_shortnames(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        logging.error(f"❌ Failed to read input file: {file_path} — {e}")
        return []

# === Read tracker to skip already uploaded ===
def read_uploaded_tracker():
    if os.path.exists(tracker_file):
        with open(tracker_file, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

# === Run uploader subprocess (Uses --test for Zenodo sandbox) ===
def run_upload(path, xml_path):
    args = ["python3", "zenodo_create.py", "--folder", path, "--test"]

    if os.path.isfile(xml_path):
        args += ["--iso_file", xml_path]

    try:
        subprocess.run(args, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# === Main Process ===
def main():
    args = parse_args()
    base_path = args.downloads
    input_file = "dataset_shortnames.txt"

    uploaded = read_uploaded_tracker()
    shortnames = read_shortnames(input_file)

    for shortname in shortnames:
        if shortname in uploaded:
            logging.info(f"⏭️  Skipping {shortname} – already uploaded")
            continue

        dataset_dir = os.path.join(base_path, shortname)
        zip_path = os.path.join(base_path, f"{shortname}.zip")
        metadata_path = os.path.join(dataset_dir, "metadata", f"{shortname}.xml")

        logging.info(f"🔍 Checking dataset: {shortname}")
        logging.info(f"    📁 Directory: {dataset_dir}")
        logging.info(f"    📄 Zip file: {zip_path}")
        logging.info(f"    🧾 Metadata XML: {metadata_path}")

        if not os.path.isdir(dataset_dir):
            msg = f"❌ Missing dataset directory for {shortname}: {dataset_dir}"
            logging.error(msg)
            failure_logger.info(msg)
            continue

        # Always upload the directory
        logging.info(f"⬆️  Uploading directory for {shortname}")
        dir_success = run_upload(dataset_dir, metadata_path)

        if dir_success:
            logging.info(f"✅ Directory upload succeeded: {shortname}")
            success_logger.info(f"{shortname} – directory uploaded")
        else:
            logging.error(f"❌ Directory upload failed: {shortname}")
            failure_logger.info(f"{shortname} – directory upload failed")
            continue  # skip ZIP if directory upload fails

        # Upload the zip if it exists
        if os.path.isfile(zip_path):
            logging.info(f"⬆️  Uploading zip for {shortname}")
            zip_success = run_upload(zip_path, metadata_path)
            if zip_success:
                logging.info(f"✅ Zip upload succeeded: {shortname}")
                success_logger.info(f"{shortname} – zip uploaded")
            else:
                logging.error(f"❌ Zip upload failed: {shortname}")
                failure_logger.info(f"{shortname} – zip upload failed")
        else:
            logging.info(f"📦 No zip found for {shortname}, only directory uploaded")

        # Mark as uploaded regardless of zip
        with open(tracker_file, "a") as f:
            f.write(shortname + "\n")

if __name__ == "__main__":
    main()
